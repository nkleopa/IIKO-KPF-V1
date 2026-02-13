"""ETL pipeline: fetches data from iiko, transforms, and upserts to DB."""

import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.db.engine import async_session
from app.models import Branch, DailyRevenue, EmployeeAttendance, SyncLog, Writeoff
from app.services.iiko_client import IikoClient
from app.services.transformers import (
    adjust_quantity,
    map_order_type,
    map_writeoff_category,
)


async def daily_sync(target_date: date | None = None, sync_type: str = "daily"):
    """Run full ETL pipeline for a single date."""
    if target_date is None:
        target_date = date.today()
        # Default: yesterday's data (complete business day)
        target_date = target_date - timedelta(days=1)

    batch_id = str(uuid.uuid4())[:8]
    date_str = target_date.isoformat()  # for iiko API (expects YYYY-MM-DD string)
    logger.info(f"[{batch_id}] Starting {sync_type} sync for {date_str}")

    async with async_session() as session:
        sync_log = SyncLog(
            batch_id=batch_id,
            sync_type=sync_type,
            status="running",
            records_processed=0,
            started_at=datetime.utcnow(),
        )
        session.add(sync_log)
        await session.commit()

        try:
            branch = await _ensure_branch(session)
            total_records = 0

            dept_id = branch.iiko_department_id
            client = IikoClient()
            async with client.session():
                # 1. Revenue (OLAP SALES)
                n = await _sync_revenue(
                    client, session, branch.id, target_date, date_str, batch_id, dept_id
                )
                total_records += n
                logger.info(f"[{batch_id}] Revenue: {n} records")

                # 2. Attendance
                n = await _sync_attendance(
                    client, session, branch.id, date_str, batch_id, dept_id
                )
                total_records += n
                logger.info(f"[{batch_id}] Attendance: {n} records")

                # 3. Write-offs
                n = await _sync_writeoffs(
                    client, session, branch.id, target_date, date_str, batch_id, dept_id
                )
                total_records += n
                logger.info(f"[{batch_id}] Write-offs: {n} records")

            sync_log.status = "success"
            sync_log.records_processed = total_records
            sync_log.completed_at = datetime.utcnow()
            await session.commit()
            logger.info(
                f"[{batch_id}] Sync complete — {total_records} records processed"
            )

        except Exception as e:
            logger.error(f"[{batch_id}] Sync failed: {e}")
            sync_log.status = "failed"
            sync_log.error_message = str(e)[:2000]
            sync_log.completed_at = datetime.utcnow()
            await session.commit()
            raise


async def _ensure_branch(session: AsyncSession) -> Branch:
    """Get or create the target branch from config."""
    from app.core.config import settings

    dept_id = settings.IIKO_DEPARTMENT_ID
    result = await session.execute(
        select(Branch).where(Branch.iiko_department_id == dept_id)
    )
    branch = result.scalar_one_or_none()
    if not branch:
        branch = Branch(
            iiko_department_id=dept_id,
            name=settings.IIKO_DEPARTMENT_NAME,
            city="Воронеж",
            is_active=True,
        )
        session.add(branch)
        await session.commit()
        await session.refresh(branch)
    return branch


def _safe_decimal(value, default: Decimal = Decimal("0")) -> Decimal:
    if value is None:
        return default
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return default


def _safe_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


async def _sync_revenue(
    client: IikoClient,
    session: AsyncSession,
    branch_id: int,
    target_date: date,
    date_str: str,
    batch_id: str,
    iiko_department_id: str | None = None,
) -> int:
    filters = {}
    if iiko_department_id:
        filters["Department.Id"] = {
            "filterType": "IncludeValues",
            "values": [iiko_department_id],
        }
    rows = await client.get_olap_report(
        report_type="SALES",
        group_fields=["OpenDate.Typed", "OrderType", "Delivery.SourceKey", "DishName"],
        agg_fields=["DishDiscountSumInt", "DishAmountInt"],
        date_from=date_str,
        date_to=date_str,
        filters=filters,
    )

    # Delete old records for this date/branch before inserting
    from sqlalchemy import and_, delete

    await session.execute(
        delete(DailyRevenue).where(
            and_(
                DailyRevenue.branch_id == branch_id,
                DailyRevenue.date == target_date,
            )
        )
    )

    count = 0
    for row in rows:
        raw_order_type = row.get("OrderType", "")
        delivery_source = row.get("Delivery.SourceKey")
        item_name = row.get("DishName")
        quantity = _safe_decimal(row.get("DishAmountInt"))
        quantity_adjusted = adjust_quantity(item_name, quantity)

        record = DailyRevenue(
            branch_id=branch_id,
            date=target_date,
            order_type=map_order_type(raw_order_type, delivery_source),
            order_type_detail=raw_order_type,
            revenue_amount=_safe_decimal(row.get("DishDiscountSumInt")),
            order_count=_safe_int(row.get("DishAmountInt")),
            item_name=item_name,
            item_quantity=quantity,
            item_quantity_adjusted=quantity_adjusted,
            sync_batch_id=batch_id,
        )
        session.add(record)
        count += 1

    await session.commit()
    return count


async def _sync_attendance(
    client: IikoClient,
    session: AsyncSession,
    branch_id: int,
    date_str: str,
    batch_id: str,
    iiko_department_id: str | None = None,
) -> int:
    records = await client.get_attendance(date_from=date_str, date_to=date_str)

    # Resolve role and employee names
    role_map = await client.get_roles()
    employee_map = await client.get_employees()

    # Delete existing attendance for this date/branch to allow re-sync
    from sqlalchemy import and_, delete

    target_date = date.fromisoformat(date_str)
    await session.execute(
        delete(EmployeeAttendance).where(
            and_(
                EmployeeAttendance.branch_id == branch_id,
                EmployeeAttendance.date_from >= datetime(
                    target_date.year, target_date.month, target_date.day
                ),
                EmployeeAttendance.date_from < datetime(
                    target_date.year, target_date.month, target_date.day
                ) + timedelta(days=1),
            )
        )
    )

    count = 0
    for rec in records:
        # Filter by department (attendance API returns ALL branches)
        if iiko_department_id and rec.get("departmentId") != iiko_department_id:
            continue

        att_id = rec.get("id")
        if not att_id:
            continue

        # Duration (Продолжительность) = dateFrom→dateTo from Attendance Journal.
        # iiko attendance XML has no "duration" field; calculate from timestamps.
        dt_from = _parse_datetime(rec.get("dateFrom", date_str))
        dt_to = _parse_datetime(rec.get("dateTo"))
        if dt_from and dt_to and dt_to > dt_from:
            worked_min = int((dt_to - dt_from).total_seconds() / 60)
        else:
            worked_min = 0
        payment_sum = _safe_decimal(rec.get("regularPaymentSum"))
        overtime_sum = _safe_decimal(rec.get("overtimePayedSum"))
        total_payment = (payment_sum + overtime_sum).quantize(Decimal("0.01"))

        emp_id = rec.get("employeeId", "")
        role_id = rec.get("roleId")

        record = EmployeeAttendance(
            iiko_attendance_id=att_id,
            branch_id=branch_id,
            employee_id=emp_id,
            employee_name=employee_map.get(emp_id),
            role_id=role_id,
            role_name=role_map.get(role_id) if role_id else None,
            date_from=dt_from,
            date_to=dt_to,
            worked_minutes=worked_min,
            worked_hours=Decimal(str(round(worked_min / 60, 2))),
            iiko_payment_sum=total_payment,
            sync_batch_id=batch_id,
        )
        session.add(record)
        count += 1

    await session.commit()
    return count


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    # iiko returns ISO 8601 with timezone like "2026-02-08T12:00:00+03:00"
    # DB column is TIMESTAMP WITHOUT TIME ZONE, so strip tzinfo
    try:
        dt = datetime.fromisoformat(value)
        return dt.replace(tzinfo=None)
    except ValueError:
        pass
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


async def _sync_writeoffs(
    client: IikoClient,
    session: AsyncSession,
    branch_id: int,
    target_date: date,
    date_str: str,
    batch_id: str,
    iiko_department_id: str | None = None,
) -> int:
    """Fetch write-off documents via /v2/documents/writeoff (PROCESSED only)."""
    from sqlalchemy import and_, delete

    # Delete old writeoff records for this date/branch
    await session.execute(
        delete(Writeoff).where(
            and_(
                Writeoff.branch_id == branch_id,
                Writeoff.date == target_date,
            )
        )
    )

    try:
        docs = await client.get_writeoff_documents(date_str, date_str)
    except Exception as e:
        logger.warning(f"Write-off documents API failed: {e} — skipping writeoffs")
        await session.commit()
        return 0

    # Resolve product and account names from iiko
    try:
        product_map = await client.get_products()
    except Exception as e:
        logger.warning(f"Product name resolution failed: {e}")
        product_map = {}

    try:
        account_entities = await client.get_entity_list(["Account"], include_deleted=True)
        account_map = {e["id"]: e.get("name", "") for e in account_entities}
    except Exception as e:
        logger.warning(f"Account name resolution failed: {e}")
        account_map = {}

    count = 0
    for doc in docs:
        # Only PROCESSED docs (API already filters, but double-check)
        if doc.get("status") != "PROCESSED":
            continue

        doc_number = doc.get("documentNumber")
        account_id = doc.get("accountId")
        account_name = account_map.get(account_id, "") if account_id else ""

        for item in doc.get("items", []):
            cost = _safe_decimal(item.get("cost"))
            product_id = item.get("productId", "unknown")
            product_name = product_map.get(product_id)
            quantity = _safe_decimal(item.get("amount"))

            record = Writeoff(
                branch_id=branch_id,
                date=target_date,
                article_name=product_id,
                category=map_writeoff_category(account_name or product_id),
                amount=cost,
                document_number=doc_number,
                account_name=account_name or None,
                product_name=product_name,
                item_quantity=quantity if quantity else None,
                sync_batch_id=batch_id,
            )
            session.add(record)
            count += 1

    await session.commit()
    return count
