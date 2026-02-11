import hashlib
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

import httpx
from lxml import etree

from app.core.config import settings
from app.core.logger import logger


class IikoAuthError(Exception):
    """Raised when iiko authentication fails."""

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"iiko auth failed (HTTP {status_code}): {detail}")


class IikoClient:
    """Async client for iiko Server API (read-only)."""

    def __init__(self):
        self._base_url = settings.IIKO_BASE_URL
        self._login = settings.IIKO_LOGIN
        self._password = settings.IIKO_PASSWORD
        self._token: str | None = None
        self._http = httpx.AsyncClient(timeout=60.0, verify=True)

    def _password_hash(self) -> str:
        # This server accepts SHA1(password) without the "resto#" prefix.
        # The docs say SHA1("resto#" + password) but cloud-hosted iiko
        # instances may differ. Tested empirically 2026-02-06.
        return hashlib.sha1(self._password.encode("utf-8")).hexdigest()

    @asynccontextmanager
    async def session(self) -> AsyncGenerator["IikoClient", None]:
        """Login on enter, logout on exit (always, even on error)."""
        await self._login_request()
        try:
            yield self
        finally:
            await self._logout()
            await self._http.aclose()

    async def _login_request(self) -> None:
        """Authenticate via form-encoded POST body (iiko requires this)."""
        url = f"{self._base_url}/resto/api/auth"
        data = {"login": self._login, "pass": self._password_hash()}
        resp = await self._http.post(url, data=data)
        if resp.status_code != 200:
            detail = resp.text.strip()
            logger.error(f"iiko auth failed (HTTP {resp.status_code}): {detail}")
            raise IikoAuthError(resp.status_code, detail)
        self._token = resp.text.strip().strip('"')
        logger.info("iiko login OK — token acquired")

    async def _logout(self) -> None:
        if not self._token:
            return
        try:
            url = f"{self._base_url}/resto/api/logout"
            # Use form body (same as auth) — this server rejects query params on POST
            resp = await self._http.post(url, data={"key": self._token})
            if resp.status_code != 200:
                # Fallback: try GET with query param
                resp = await self._http.get(url, params={"key": self._token})
            logger.info("iiko logout OK — license released")
        except Exception as e:
            logger.warning(f"iiko logout failed: {e}")
        finally:
            self._token = None

    async def get_olap_report(
        self,
        report_type: str,
        group_fields: list[str],
        agg_fields: list[str],
        date_from: str,
        date_to: str,
        filters: dict[str, Any] | None = None,
    ) -> list[dict]:
        """Fetch OLAP report. Dates in YYYY-MM-DD format."""
        url = f"{self._base_url}/resto/api/v2/reports/olap"
        body: dict[str, Any] = {
            "reportType": report_type,
            "groupByRowFields": group_fields,
            "aggregateFields": agg_fields,
            "filters": {
                "OpenDate.Typed": {
                    "filterType": "DateRange",
                    "periodType": "CUSTOM",
                    "from": date_from,
                    "to": date_to,
                    "includeLow": True,
                    "includeHigh": True,
                },
                "DeletedWithWriteoff": {
                    "filterType": "IncludeValues",
                    "values": ["NOT_DELETED"],
                },
                "OrderDeleted": {
                    "filterType": "IncludeValues",
                    "values": ["NOT_DELETED"],
                },
                **(filters or {}),
            },
        }
        resp = await self._http.post(url, params={"key": self._token}, json=body)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", [])

    async def get_attendance(self, date_from: str, date_to: str) -> list[dict]:
        """Fetch employee attendance. Returns parsed XML as list of dicts."""
        url = f"{self._base_url}/resto/api/employees/attendance"
        params = {
            "key": self._token,
            "from": date_from,
            "to": date_to,
            "withPaymentDetails": "true",
        }
        resp = await self._http.get(url, params=params)
        resp.raise_for_status()
        return self._parse_attendance_xml(resp.content)

    @staticmethod
    def _parse_attendance_xml(xml_bytes: bytes) -> list[dict]:
        """Parse iiko attendance XML into list of dicts.

        XML uses <attendance> elements (not <attendanceRecord>).
        paymentDetails is a flat group of sub-elements, not a list.
        """
        root = etree.fromstring(xml_bytes)
        records = []
        for item in root.findall(".//attendance"):
            record: dict[str, str | None] = {}
            for child in item:
                if child.tag == "paymentDetails":
                    # Flatten paymentDetails sub-fields
                    for pd_child in child:
                        record[pd_child.tag] = pd_child.text
                else:
                    record[child.tag] = child.text
            records.append(record)
        return records

    async def get_departments(self) -> list[dict]:
        """Fetch corporation department hierarchy (XML → list of dicts)."""
        url = f"{self._base_url}/resto/api/corporation/departments"
        resp = await self._http.get(url, params={"key": self._token})
        resp.raise_for_status()
        return self._parse_departments_xml(resp.content)

    @staticmethod
    def _parse_departments_xml(xml_bytes: bytes) -> list[dict]:
        """Parse corporateItemDto XML into list of dicts."""
        root = etree.fromstring(xml_bytes)
        departments = []
        for item in root.findall(".//corporateItemDto"):
            dept: dict[str, str | None] = {}
            for child in item:
                dept[child.tag] = child.text
            departments.append(dept)
        return departments

    async def get_entity_list(
        self, root_types: list[str], include_deleted: bool = False
    ) -> list[dict]:
        """Fetch reference entities (OrderType, PaymentType, etc.) via v2 JSON API."""
        url = f"{self._base_url}/resto/api/v2/entities/list"
        params: list[tuple[str, str]] = [("key", self._token or "")]
        for rt in root_types:
            params.append(("rootType", rt))
        params.append(("includeDeleted", str(include_deleted).lower()))
        resp = await self._http.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    async def get_olap_columns(self, report_type: str) -> list[dict]:
        url = f"{self._base_url}/resto/api/v2/reports/olap/columns"
        resp = await self._http.get(
            url, params={"key": self._token, "reportType": report_type}
        )
        resp.raise_for_status()
        return resp.json()

    async def get_olap_presets(self) -> list[dict]:
        url = f"{self._base_url}/resto/api/v2/reports/olap/presets"
        resp = await self._http.get(url, params={"key": self._token})
        resp.raise_for_status()
        return resp.json()

    async def get_roles(self) -> dict[str, str]:
        """Fetch role ID → role name mapping from /resto/api/employees/roles."""
        url = f"{self._base_url}/resto/api/employees/roles"
        resp = await self._http.get(url, params={"key": self._token})
        resp.raise_for_status()
        root = etree.fromstring(resp.content)
        roles: dict[str, str] = {}
        for role in root.findall(".//role"):
            role_id = role.findtext("id")
            role_name = role.findtext("name")
            if role_id and role_name:
                roles[role_id] = role_name
        return roles

    async def get_employees(self) -> dict[str, str]:
        """Fetch employee ID → name mapping from /resto/api/employees."""
        url = f"{self._base_url}/resto/api/employees"
        resp = await self._http.get(url, params={"key": self._token})
        resp.raise_for_status()
        root = etree.fromstring(resp.content)
        employees: dict[str, str] = {}
        for emp in root.findall(".//employee"):
            emp_id = emp.findtext("id")
            emp_name = emp.findtext("name")
            if emp_id and emp_name:
                employees[emp_id] = emp_name
        return employees

    async def get_writeoff_documents(
        self, date_from: str, date_to: str
    ) -> list[dict]:
        """Fetch write-off acts via /resto/api/v2/documents/writeoff (JSON)."""
        url = f"{self._base_url}/resto/api/v2/documents/writeoff"
        params = {
            "key": self._token,
            "dateFrom": date_from,
            "dateTo": date_to,
            "status": "PROCESSED",
        }
        resp = await self._http.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", [])

    async def check_licence(self) -> str:
        """Check licence slot availability (no auth required)."""
        url = f"{self._base_url}/resto/api/licence/info"
        resp = await self._http.get(url)
        resp.raise_for_status()
        return resp.text.strip()
