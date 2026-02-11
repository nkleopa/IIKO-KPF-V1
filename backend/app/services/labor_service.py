from datetime import date
from decimal import Decimal

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import EmployeeAttendance, StaffRate
from app.services.transformers import is_excluded_role, is_kitchen_role


async def get_labor(
    session: AsyncSession, branch_id: int, date_from: date, date_to: date
) -> list[dict]:
    """Get labor cost per employee, joining attendance with SCD2 rates."""
    att_result = await session.execute(
        select(EmployeeAttendance)
        .where(
            and_(
                EmployeeAttendance.branch_id == branch_id,
                func.date(EmployeeAttendance.date_from) >= date_from,
                func.date(EmployeeAttendance.date_from) <= date_to,
            )
        )
        .order_by(EmployeeAttendance.employee_name)
    )
    attendances = att_result.scalars().all()

    # Aggregate hours per employee, excluding manager roles in Python
    emp_hours: dict[str, dict] = {}
    for att in attendances:
        if is_excluded_role(att.role_name):
            continue
        eid = att.employee_id
        if eid not in emp_hours:
            emp_hours[eid] = {
                "employee_name": att.employee_name or eid,
                "role_name": att.role_name,
                "total_hours": Decimal("0"),
            }
        emp_hours[eid]["total_hours"] += att.worked_hours

    # Get current rates for each employee
    rows = []
    for eid, data in emp_hours.items():
        rate_result = await session.execute(
            select(StaffRate)
            .where(
                and_(
                    StaffRate.employee_id == eid,
                    StaffRate.branch_id == branch_id,
                    StaffRate.valid_from <= date_to,
                    (StaffRate.valid_to > date_from) | (StaffRate.valid_to.is_(None)),
                )
            )
            .order_by(StaffRate.valid_from.desc())
            .limit(1)
        )
        rate = rate_result.scalar_one_or_none()
        hourly_rate = rate.hourly_rate if rate else Decimal("0")
        labor_cost = data["total_hours"] * hourly_rate

        rows.append(
            {
                "employee_name": data["employee_name"],
                "role_name": data["role_name"],
                "total_hours": data["total_hours"],
                "hourly_rate": hourly_rate,
                "labor_cost": labor_cost,
            }
        )

    return rows


async def get_labor_total(
    session: AsyncSession, branch_id: int, date_from: date, date_to: date
) -> Decimal:
    """Total labor cost for the period."""
    rows = await get_labor(session, branch_id, date_from, date_to)
    return sum((r["labor_cost"] for r in rows), Decimal("0"))


async def get_kitchen_labor_total(
    session: AsyncSession, branch_id: int, date_from: date, date_to: date
) -> Decimal:
    """Kitchen labor cost only (Повар*, Мангал*) for KC%."""
    rows = await get_labor(session, branch_id, date_from, date_to)
    return sum(
        (r["labor_cost"] for r in rows if is_kitchen_role(r["role_name"])),
        Decimal("0"),
    )
