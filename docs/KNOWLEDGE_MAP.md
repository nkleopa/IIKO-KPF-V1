# KPF Knowledge Map

> Links business requirements (KPF metrics) to specific iiko API endpoints and local documentation files.

---

## Revenue Metrics

| Requirement | API Endpoint | Method | Doc File |
|------------|-------------|--------|----------|
| Total revenue by date | `/resto/api/v2/reports/olap` | POST (SALES, `DishSumInt`) | `olap-otchety-v2.txt` |
| Revenue by order type (delivery/hall) | `/resto/api/v2/reports/olap` | POST (SALES, group by `OrderType`) | `primery-vyzova-olap-otchet-v2.txt` |
| Revenue by dish/item | `/resto/api/v2/reports/olap` | POST (SALES, group by `DishName`) | `primery-vyzova-olap-otchet-v2.txt` |
| Order count by date | `/resto/api/v2/reports/olap` | POST (SALES, `UniqOrderId`) | `olap-otchety-v2.txt` |
| Guest count | `/resto/api/v2/reports/olap` | POST (SALES, `GuestNum`) | `olap-otchety-v2.txt` |
| Available OLAP columns | `/resto/api/v2/reports/olap/columns` | GET (`reportType=SALES`) | `olap-otchety-v2.txt` |
| Preset reports | `/resto/api/v2/reports/olap/presets` | GET | `prednastroennye-olap-otchety-vv2.txt` |
| OLAP report formation guide | — | — | `formirovanie-olap-otcheta-v-api.txt` |

## Labor Cost Metrics

| Requirement | API Endpoint | Method | Doc File |
|------------|-------------|--------|----------|
| Employee attendance (shifts) | `/resto/api/employees/attendance` | GET (XML) | `rabota-s-dannymi-yavok.txt` |
| Attendance by department | `/resto/api/employees/attendance/department/{id}/` | GET (XML) | `rabota-s-dannymi-yavok.txt` |
| Worked minutes & pay details | `attendance?withPaymentDetails=true` | GET (XML) | `rabota-s-dannymi-yavok.txt` |
| Employee salary (monthly) | `/resto/api/employees/salary` | GET (XML) | `rabota-s-dannymi-oklada.txt` |
| Salary by employee on date | `/resto/api/employees/salary/byId/{uuid}/{date}` | GET (XML) | `rabota-s-dannymi-oklada.txt` |
| Employee data | `/resto/api/employees` | GET (XML) | `rabota-s-dannymi-sotrudnikovv.txt` |
| Positions/roles | `/resto/api/employees/roles` | GET (XML) | `rabota-s-dannymi-dolzhnostey.txt` |
| Shift schedules | `/resto/api/employees/schedules` | GET (XML) | `rabota-s-dannymi-smeny-i-raspisaniy.txt` |
| Employee availability | `/resto/api/employees/availability/list` | GET (XML) | `rabota-s-dannymi-yavok.txt` |

## Write-off Metrics

| Requirement | API Endpoint | Method | Doc File |
|------------|-------------|--------|----------|
| Write-off acts | `/resto/api/documents/writeoff/...` | GET (XML) | `akty-spisaniya.txt` |
| Write-offs via OLAP (TRANSACTIONS) | `/resto/api/v2/reports/olap` | POST (`TRANSACTIONS`) | `olap-otchety-v2.txt`, `otchety-v1.txt` |
| Internal transfers | `/resto/api/documents/internalTransfer/...` | GET (XML) | `vnutrennie-peremescheniya.txt` |

## Authentication & Session

| Requirement | API Endpoint | Method | Doc File |
|------------|-------------|--------|----------|
| Login (get token) | `/resto/api/auth` | POST (form-encoded) | `avtorizatsiya.txt` |
| Logout (release license) | `/resto/api/logout` | POST | `avtorizatsiya.txt` |
| License slot info | `/resto/api/licence/info` | GET | `opisanie-oshibok.txt` |
| Error handling | — | — | `opisanie-oshibok.txt` |
| API constraints | — | — | `ogranicheniya-i-rekomendatsii.txt` |
| API principles | — | — | `printsipy-raboty.txt` |

## Supporting Reference

| Topic | Doc File | Notes |
|-------|----------|-------|
| Base type codes (OrderType enum values, etc.) | `kody-bazovykh-tipov.txt` | **Critical** for OrderType mapping |
| Directories/references | `spravochniki.txt` | Departments, stores, etc. |
| Corporation/chain setup | `korporatsii.txt` | Multi-branch architecture |
| Price categories | `tsenovye-kategorii.txt` | Menu pricing |
| Accounting periods | `periody-deystviya.txt` | Fiscal periods |

---

## Quick Reference: Our Sync Pipeline

```
daily_sync(yesterday)
  │
  ├─ 1. POST /resto/api/auth  →  token
  │     (form-encoded: login + SHA1("resto#" + password))
  │
  ├─ 2. POST /resto/api/v2/reports/olap  →  revenue data
  │     (SALES report, group by OpenDate.Typed + OrderType + DishName)
  │     (aggregate DishSumInt + DishAmountInt)
  │     (filter: DeletedWithWriteoff, OrderDeleted, OpenDate.Typed)
  │     Doc: olap-otchety-v2.txt, primery-vyzova-olap-otchet-v2.txt
  │
  ├─ 3. GET /resto/api/employees/attendance  →  attendance XML
  │     (?from=YYYY-MM-DD&to=YYYY-MM-DD&withPaymentDetails=true)
  │     Doc: rabota-s-dannymi-yavok.txt
  │
  ├─ 4. POST /resto/api/v2/reports/olap  →  write-off data (TBD)
  │     (TRANSACTIONS report, filter by write-off account types)
  │     Doc: olap-otchety-v2.txt, akty-spisaniya.txt
  │
  └─ 5. POST /resto/api/logout  →  release license
        Doc: avtorizatsiya.txt
```

---

## File Index

All documentation files are in `docs/iiko_api_raw/`:

```
docs/iiko_api_raw/
├── {slug}.html          # Raw HTML (54 files)
├── {slug}.txt           # Stripped text (54 files)
└── iiko_api_db.json     # Structured index with metadata

IIKO_MASTER_REFERENCE.md  # Single searchable 1.5MB document
IIKO_KNOWLEDGE_BASE.md    # Curated knowledge base (manual)
```
