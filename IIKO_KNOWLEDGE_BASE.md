# iiko API Knowledge Base

> Single source of truth for iiko API integration in the KPF Dashboard project.
> Source: https://ru.iiko.help/articles/#!api-documentations/

---

## Table of Contents

1. [API Product Overview](#1-api-product-overview)
2. [iikoServer API (REST API v1/v2)](#2-iikoserver-api)
3. [Authentication](#3-authentication)
4. [Constraints & Recommendations](#4-constraints--recommendations)
5. [Error Codes](#5-error-codes)
6. [OLAP Reports v2](#6-olap-reports-v2)
7. [OLAP Sales Examples](#7-olap-sales-examples)
8. [Employee Attendance](#8-employee-attendance)
9. [Employee Salary](#9-employee-salary)
10. [Schema Mapping to PostgreSQL](#10-schema-mapping-to-postgresql)
11. [KPF Calculation Methods](#11-kpf-calculation-methods)

---

## 1. API Product Overview

iiko provides **four** distinct API products:

| API | Purpose | Our Usage |
|-----|---------|-----------|
| **iikoServer API** (REST v1/v2) | Back-office: OLAP reports, employees, attendance, nomenclature, documents | **PRIMARY** - all KPF data |
| **iikoFront API** | POS terminal plugins (C#/.NET, runs locally on cash register) | Not used |
| **iikoCloud API** | Cloud orchestration for delivery, table reservations, loyalty | Not used |
| **iikoPublic API** | External menus, online ordering | Not used |

**We only use iikoServer API** (REST v1 for attendance/salary, REST v2 for OLAP reports).

---

## 2. iikoServer API

### Base URL Pattern

```
https://{host}:{port}/resto/api/...
```

- Cloud-hosted instances: `https://{account-id}.iiko.it/resto/api/...` (internal DNS, may not resolve publicly)
- On-premise instances: `https://{server-ip}:8080/resto/api/...` (default port 8080)

### Principles of Work

- Entities are represented as **XML documents** (v1) or **JSON** (v2 OLAP)
- Lists of entities are XML documents with root element containing entity child elements
- POST creation uses `Content-Type: application/x-www-form-urlencoded`
- PUT updates use `Content-Type: application/xml`
- Successful creation returns HTTP **201** (Created)
- Successful update returns HTTP **200** (OK)

### API Versions

- **v1** (`/resto/api/...`): Employee data, attendance, salary, nomenclature, documents. Returns XML.
- **v2** (`/resto/api/v2/...`): OLAP reports only. Returns JSON.

---

## 3. Authentication

### Login

```
POST https://{host}:{port}/resto/api/auth
Content-Type: application/x-www-form-urlencoded

login={login}&pass={sha1passwordhash}
```

**Password hash**: `SHA1("resto#" + password)`

```bash
# Example: password = "test"
printf "resto#test" | sha1sum
# Result: 2155245b2c002a1986d3f384af93be813537a476
```

**Response**: Plain text string token (e.g., `b354d18c-3d3a-e1a6-c3b9-9ef7b5055318`)

**Token usage**: Pass as query parameter `?key={token}` or as cookie `key={token}` in all subsequent requests. Since iiko 4.3, the server sets the cookie automatically.

### Logout

```
POST https://{host}:{port}/resto/api/logout?key={token}
```

or with cookie: `POST /resto/api/logout` with cookie `key={token}`

### License Warning

> **CRITICAL**: Login occupies one license slot. The token remains valid until it expires or the server restarts. If you have only one license and already obtained a token, the next login attempt will **fail with an error**. Always logout to release the license. If you cannot store the token, logout immediately after use.

### Session Timeout

- Default timeout: **1 hour** from login or last request
- Token refresh is **not implemented** in REST API v1/v2
- Server restart invalidates all tokens

### License Slot Info

Check available license slots:
```
GET /resto/api/licence/info?moduleId=28008806
```

---

## 4. Constraints & Recommendations

1. **Sequential requests only** - Each request must complete before sending the next one. No concurrent requests.
2. **Max date range: 1 month** - Ideally query one day or one week at a time.
3. **OLAP `build-summary=false`** - If you don't need summary totals, set `buildSummary: false`. For large chains, `true` can hang the server. (Default changed to `false` in iiko 9.1.2)
4. **Max 7 OLAP fields** - Use no more than 7 fields in OLAP report queries (groupBy + aggregate combined).
5. **Test on demo server first** - Always validate queries on the demo instance before running on production.

---

## 5. Error Codes

All REST API v1 and v2 methods may return these errors with `text/plain` body:

| HTTP Code | Meaning | Action |
|-----------|---------|--------|
| **400** | Bad request - wrong parameter types, deserialization errors, incomplete data. Examples: `Wrong date format: 2019-0513 15:26`, `Malformed Product id: ''` | Fix request parameters |
| **401** | Not authenticated: no `key` parameter/cookie, session timeout (~1 hour), server restarted, server starting up | Re-authenticate (login again) |
| **403** | Access denied: no license for API module (`Module %s is blocked within current license`), license slots exhausted (`License enhancement is required: no connections available for module %s`), insufficient permissions (`Permission denied`) | Check license, contact admin |
| **404** | Object not found, incorrect path | Fix URL |
| **409** | Business logic error - server returns user-readable message. Examples: `"Доступ запрещен КОД_ПРАВА"`, `"Операция создает приход на отрицательные остатки..."`, `"У вас нет права изменять документы задним числом."` | Show error text to user |
| **500** | Internal server error. Examples: `User represents store, but no linked store found`, `java.net.SocketException: Connection reset`, `product == null` | Log error, contact iiko support |

**Important notes:**
- Error body is `text/plain` - show to user for 409, log for all others
- `text/html` response indicates network/config error (wrong URL, DNS, proxy, empty Tomcat)
- Error text is **not localized** (except 409) and may contain UUIDs
- Text may contain mandatory newlines (use CSS `white-space: pre-line`)
- Text is **not escaped** - may contain dangerous chars for JS, HTML, SQL

---

## 6. OLAP Reports v2

### Get Available Columns

```
GET /resto/api/v2/reports/olap/columns?key={token}&reportType={type}
```

**Report types**: `SALES` | `TRANSACTIONS` | `DELIVERIES`

**Response**: JSON object mapping field names to their metadata:

```json
{
  "FieldName": {
    "name": "Display name in iikoOffice",
    "type": "ENUM|STRING|ID|DATETIME|INTEGER|PERCENT|DURATION_IN_SECONDS|AMOUNT|MONEY",
    "aggregationAllowed": true,
    "groupingAllowed": true,
    "filteringAllowed": true,
    "tags": ["Category1", "Category2"]
  }
}
```

**Field types:**
- `ENUM` - Enumerated values (filterable by value)
- `STRING` - Text (filterable by value)
- `ID` - Internal iiko UUID (since 5.0)
- `DATETIME` - Date and time
- `INTEGER` - Integer
- `PERCENT` - Percentage (0 to 1)
- `DURATION_IN_SECONDS` - Duration in seconds
- `AMOUNT` - Quantity
- `MONEY` - Monetary sum

### Build OLAP Report

```
POST /resto/api/v2/reports/olap?key={token}
Content-Type: Application/json; charset=utf-8
```

**Request body:**

```json
{
  "reportType": "SALES",
  "buildSummary": false,
  "groupByRowFields": ["FieldName1", "FieldName2"],
  "groupByColFields": ["FieldName3"],
  "aggregateFields": ["FieldName4", "FieldName5"],
  "filters": {
    "OpenDate.Typed": {
      "filterType": "DateRange",
      "periodType": "CUSTOM",
      "from": "2024-01-01",
      "to": "2024-01-31",
      "includeLow": true,
      "includeHigh": true
    }
  }
}
```

**Parameters:**

| Field | Required | Description |
|-------|----------|-------------|
| `reportType` | Yes | `SALES`, `TRANSACTIONS`, or `DELIVERIES` |
| `buildSummary` | No | Calculate totals. Default: `true` (pre-9.1.2), `false` (9.1.2+). Since iiko 5.3.4. |
| `groupByRowFields` | Yes | Fields with `groupingAllowed=true` |
| `groupByColFields` | No | Optional column grouping |
| `aggregateFields` | Yes | Fields with `aggregationAllowed=true` |
| `filters` | Yes | Filter object. **Since iiko 5.5, date filter is mandatory.** |

### Filter Types

#### Value Filter (for ENUM, STRING)

```json
"FieldName": {
  "filterType": "IncludeValues",
  "values": ["Value1", "Value2"]
}
```
- `IncludeValues` - include only listed values
- `ExcludeValues` - exclude listed values

#### Range Filter (for INTEGER, PERCENT, AMOUNT, MONEY)

```json
"FieldName": {
  "filterType": "Range",
  "from": 100,
  "to": 500,
  "includeLow": true,
  "includeHigh": false
}
```

#### Date Filter (for DATETIME, DATE)

```json
"OpenDate.Typed": {
  "filterType": "DateRange",
  "periodType": "CUSTOM",
  "from": "2024-01-01",
  "to": "2024-01-31",
  "includeLow": true,
  "includeHigh": true
}
```

**Period types:** `CUSTOM`, `OPEN_PERIOD`, `TODAY`, `YESTERDAY`, `CURRENT_WEEK`, `CURRENT_MONTH`, `CURRENT_YEAR`, `LAST_WEEK`, `LAST_MONTH`, `LAST_YEAR`

**Important:** For `CUSTOM`, `from` and `to` are used. For other period types, only `from` is required (value can be anything). Date format: `yyyy-MM-dd` or `yyyy-MM-dd'T'HH:mm:ss.SSS`.

#### Date+Time Filter

Combine `OpenDate.Typed` (date) with `OpenTime` (time):

```json
"filters": {
  "OpenDate.Typed": {
    "filterType": "DateRange",
    "periodType": "CUSTOM",
    "from": "2024-01-01",
    "to": "2024-01-01",
    "includeLow": true,
    "includeHigh": true
  },
  "OpenTime": {
    "filterType": "DateRange",
    "periodType": "CUSTOM",
    "from": "2024-01-01T01:00:00.000",
    "to": "2024-01-01T23:00:00.000",
    "includeLow": true,
    "includeHigh": true
  }
}
```

### Date Field Selection

| Report Type | Recommended Date Field |
|-------------|----------------------|
| `SALES` | `OpenDate.Typed` |
| `DELIVERIES` | `OpenDate.Typed` |
| `TRANSACTIONS` | `DateTime.DateTyped` (date) or `DateTime.Typed` (datetime) |
| iiko 4.1 (old) | `OpenDate` / `DateTime.OperDayFilter` |

### Response Format

```json
{
  "data": [
    {
      "GroupField1": "Value1",
      "GroupField2": "Value2",
      "AggField1": 12345.67,
      "AggField2": 42
    }
  ],
  "summary": [
    [{"GroupField1": "Value1"}, {"AggField1": 12345.67}],
    [{}, {"AggField1": 99999.99}]
  ]
}
```

- `data` - Linear report rows, each object = one row in iikoOffice grid
- `summary` - List of [grouping_keys, aggregate_totals] pairs. Empty first object = grand totals. Empty when `buildSummary=false`.

### Preset Reports

```
GET /resto/api/v2/reports/olap/presets?key={token}
```

Returns list of saved report configurations. Can run by preset ID.

### Performance Warning

> Fields computing start balance (`StartBalance.Amount`, `StartBalance.Money`, `FinalBalance.Amount`, `FinalBalance.Money`) scan the **entire** transaction table of the database with no optimizations. Use the Balance Reports API (since 5.2) instead. Since 5.5, OLAP balance queries are optimized when using appropriate groupings/filters from ATransactionSum/ATransactionBalance tables.

---

## 7. OLAP Sales Examples

### Revenue by Payment Types

```json
{
  "reportType": "SALES",
  "groupByRowFields": ["PayTypes", "OpenDate"],
  "aggregateFields": ["GuestNum", "DishSumInt", "DishDiscountSumInt", "UniqOrderId"],
  "filters": {
    "OpenDate": {
      "filterType": "DateRange",
      "periodType": "CUSTOM",
      "from": "2024-01-01T00:00:00.000",
      "to": "2024-01-31T00:00:00.000"
    },
    "DeletedWithWriteoff": {
      "filterType": "ExcludeValues",
      "values": ["DELETED_WITH_WRITEOFF", "DELETED_WITHOUT_WRITEOFF"]
    },
    "OrderDeleted": {
      "filterType": "IncludeValues",
      "values": ["NOT_DELETED"]
    }
  }
}
```

### Revenue by Days (Simple)

```json
{
  "reportType": "SALES",
  "groupByRowFields": ["OpenDate"],
  "aggregateFields": ["GuestNum", "DishSumInt", "DishDiscountSumInt", "UniqOrderId"],
  "filters": {
    "OpenDate": {
      "filterType": "DateRange",
      "periodType": "CUSTOM",
      "from": "2024-01-01T00:00:00.000",
      "to": "2024-01-31T00:00:00.000"
    },
    "DeletedWithWriteoff": {
      "filterType": "IncludeValues",
      "values": ["NOT_DELETED"]
    },
    "OrderDeleted": {
      "filterType": "IncludeValues",
      "values": ["NOT_DELETED"]
    }
  }
}
```

**Response example:**

```json
{
  "data": [
    {
      "DishDiscountSumInt": 186521.5,
      "DishSumInt": 198795,
      "GuestNum": 186,
      "OpenDate": "2014.01.01",
      "UniqOrderId": 196
    },
    {
      "DishDiscountSumInt": 279318,
      "DishSumInt": 292240,
      "GuestNum": 271,
      "OpenDate": "2014.01.02",
      "UniqOrderId": 286
    }
  ]
}
```

### Key OLAP Fields for KPF

**Revenue fields (SALES report):**

| Field Name | Description | Type |
|-----------|-------------|------|
| `OpenDate.Typed` | Business day date | DATE (filter) |
| `OpenDate` | Business day (display) | DATE (group) |
| `OrderType` | Order type (hall/delivery/etc) | ENUM (group/filter) |
| `DishName` | Dish name | STRING (group) |
| `DishSumInt` | Dish sum (revenue) | MONEY (aggregate) |
| `DishDiscountSumInt` | Sum with discounts | MONEY (aggregate) |
| `DishAmountInt` | Dish quantity | AMOUNT (aggregate) |
| `GuestNum` | Guest count | INTEGER (aggregate) |
| `UniqOrderId` | Unique order count | INTEGER (aggregate) |
| `PayTypes` | Payment type | ENUM (group/filter) |
| `DeletedWithWriteoff` | Deletion status | ENUM (filter) |
| `OrderDeleted` | Order deletion status | ENUM (filter) |
| `Department` | Department name | STRING (group/filter) |
| `Department.Id` | Department UUID | ID (filter, since 5.0) |

**Standard filters to exclude deleted items:**

```json
"DeletedWithWriteoff": {
  "filterType": "ExcludeValues",
  "values": ["DELETED_WITH_WRITEOFF", "DELETED_WITHOUT_WRITEOFF"]
},
"OrderDeleted": {
  "filterType": "IncludeValues",
  "values": ["NOT_DELETED"]
}
```

---

## 8. Employee Attendance

### Get Attendance Types

```
GET /resto/api/employees/attendance/types?key={token}
```

Parameters: `includeDeleted` (bool, default false), `revisionFrom` (int, since 6.4)

### Get Attendance Records

```
GET /resto/api/employees/attendance?key={token}&from={YYYY-MM-DD}&to={YYYY-MM-DD}&withPaymentDetails=true
```

**Variations with filters:**
- By employee: `/resto/api/employees/attendance/byEmployee/{employeeUUID}/`
- By department (code): `/resto/api/employees/attendance/byDepartment/{departmentCode}/`
- By department (ID): `/resto/api/employees/attendance/department/{departmentId}/`
- Combined: `/byDepartment/{code}/byEmployee/{uuid}/` or `/department/{id}/byEmployee/{uuid}/`

**Parameters:**

| Parameter | Description |
|-----------|-------------|
| `from` | Start date (inclusive), `YYYY-MM-DD` |
| `to` | End date (**inclusive** - unlike other APIs), `YYYY-MM-DD` |
| `withPaymentDetails` | (since 5.0) Include worked time and salary data. Empty for salaried/scheduled employees. |
| `revisionFrom` | Revision number for incremental sync (default -1) |

**Important:** The `to` date is **inclusive**. `&to=2016-03-21` returns attendance intersecting `2016-03-22 00:00:00`.

### Response XML Schema

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<attendances>
  <attendance>
    <id>faa6d21e-7193-4c1f-885c-6049ddddd0ce</id>
    <employeeId>0a508f8c-4cdb-4126-bd0d-243c4718c22f</employeeId>
    <roleId>6e3fa11d-3617-c735-bd29-aeac662741ed</roleId>
    <dateFrom>2017-09-21T10:27:00+03:00</dateFrom>
    <dateTo>2017-09-21T14:02:00+03:00</dateTo>
    <attendanceType>W</attendanceType>
    <comment/>
    <departmentId>2b602c10-2045-4f52-b5f9-d00be812d6aa</departmentId>
    <departmentName>ТП1</departmentName>
    <paymentDetails>
      <regularPayedMinutes>300</regularPayedMinutes>
      <regularPaymentSum>50.000000000</regularPaymentSum>
      <overtimePayedMinutes>0</overtimePayedMinutes>
      <overtimePayedSum>0</overtimePayedSum>
      <otherPaymentsSum>0</otherPaymentsSum>
    </paymentDetails>
    <personalDateFrom>2017-09-21T09:02:00+03:00</personalDateFrom>
    <created>2017-09-21T09:02:40.343+03:00</created>
    <modified>2017-09-21T10:17:06.620+03:00</modified>
    <userModified>c831367e-778f-e80f-18f7-bd0843cd10c6</userModified>
  </attendance>
</attendances>
```

**Key attendance fields:**

| XML Element | Description |
|-------------|-------------|
| `id` | Attendance record UUID |
| `employeeId` | Employee UUID |
| `roleId` | Role/position UUID |
| `dateFrom` | Shift start (ISO 8601 with timezone) |
| `dateTo` | Shift end (null if still open) |
| `attendanceType` | Type code (`W` = work, etc.) |
| `departmentId` | Department UUID |
| `departmentName` | Department name |
| `paymentDetails.regularPayedMinutes` | Regular worked minutes |
| `paymentDetails.regularPaymentSum` | Regular pay sum |
| `paymentDetails.overtimePayedMinutes` | Overtime minutes |
| `paymentDetails.overtimePayedSum` | Overtime pay sum |
| `paymentDetails.otherPaymentsSum` | Other payments |
| `personalDateFrom` | Personal clock-in time |
| `created` | Record creation timestamp |
| `modified` | Last modification timestamp |

**Note:** For salaried/scheduled employees, `paymentDetails` will be **empty** - their pay is not calculated per-attendance.

### Employee Availability

```
GET /resto/api/employees/availability/list?key={token}&from={YYYY-MM-DD}&to={YYYY-MM-DD}&department={uuid}&role={uuid}&user={uuid}
```

Returns schedule-based availability periods. `to` is **exclusive** (unlike attendance). Multiple department/role/user params supported.

---

## 9. Employee Salary

### Get Salary by Employee ID

```
GET /resto/api/employees/salary/byId/{employeeUUID}?key={token}
```

### Get Salary by Employee ID on Date

```
GET /resto/api/employees/salary/byId/{employeeUUID}/{YYYY-MM-DD}?key={token}
```

### List All Salaries

```
GET /resto/api/employees/salary?key={token}
```

Parameters: `revisionFrom` (int, since 6.4)

Returns: List of salaries for non-deleted employees.

### Set Salary

```
POST /resto/api/employees/salary/byId/{employeeUUID}/{YYYY-MM-DD}?key={token}&payment={amount}
```

Since iiko 4.0. Sets salary effective from the given date.

---

## 10. Schema Mapping to PostgreSQL

### Revenue (OLAP SALES -> `daily_revenue`)

| iiko OLAP Field | PostgreSQL Column | Notes |
|----------------|-------------------|-------|
| `OpenDate.Typed` / `OpenDate` | `date` | Filter + group field |
| `OrderType` | `order_type_detail` / `order_type` | Raw value -> mapped (delivery/hall) |
| `DishName` | `item_name` | For Dyuzhina rule |
| `DishSumInt` | `revenue_amount` | Total dish sum |
| `DishAmountInt` | `item_quantity` / `item_quantity_adjusted` | Raw qty, adjusted for Dyuzhina |
| `UniqOrderId` | `order_count` | Unique orders |
| `Department.Id` | `branch_id` (via Branch lookup) | Filter by department |

**Our OLAP query for revenue sync:**

```json
{
  "reportType": "SALES",
  "buildSummary": false,
  "groupByRowFields": ["OpenDate.Typed", "OrderType", "DishName"],
  "aggregateFields": ["DishSumInt", "DishAmountInt"],
  "filters": {
    "OpenDate.Typed": {
      "filterType": "DateRange",
      "periodType": "CUSTOM",
      "from": "{date_from}",
      "to": "{date_to}",
      "includeLow": true,
      "includeHigh": true
    },
    "DeletedWithWriteoff": {
      "filterType": "ExcludeValues",
      "values": ["DELETED_WITH_WRITEOFF", "DELETED_WITHOUT_WRITEOFF"]
    },
    "OrderDeleted": {
      "filterType": "IncludeValues",
      "values": ["NOT_DELETED"]
    }
  }
}
```

**Total fields: 5** (3 group + 2 aggregate) - within the 7-field limit.

### Attendance (XML -> `employee_attendance`)

| XML Element | PostgreSQL Column | Notes |
|-------------|-------------------|-------|
| `id` | `iiko_attendance_id` | Unique constraint |
| `employeeId` | `employee_id` | Employee UUID from iiko |
| `roleId` | `role_id` | Role UUID |
| `dateFrom` | `date_from` | Shift start |
| `dateTo` | `date_to` | Shift end (nullable) |
| `paymentDetails.regularPayedMinutes` | `worked_minutes` | Minutes worked |
| computed | `worked_hours` | `worked_minutes / 60.0` |
| `paymentDetails.regularPaymentSum` | `iiko_payment_sum` | iiko-computed pay |
| `departmentId` | `branch_id` (via Branch lookup) | Department mapping |

### Salary (XML -> `staff_rates` SCD Type 2)

| iiko Salary API | PostgreSQL Column | Notes |
|-----------------|-------------------|-------|
| `employeeUUID` | `employee_id` | Business key |
| Employee name (from employees API) | `employee_name` | Display name |
| Department | `branch_id` | FK to branches |
| `payment` | `hourly_rate` | **Requires conversion** - iiko stores monthly salary, we need hourly |
| Effective date | `valid_from` | SCD start date |
| Next rate's date | `valid_to` | SCD end date (null = current) |

**Important:** iiko salary API returns **monthly salary** (оклад), not hourly rate. Conversion needed:
- If employee is hourly: rate is per-hour in iiko
- If employee is salaried: need to divide by expected monthly hours (e.g., 168h for full-time)
- This mapping depends on the restaurant's pay structure and must be configured per-branch

---

## 11. KPF Calculation Methods

### Data Sources

| Metric | iiko Source | API | Notes |
|--------|-----------|-----|-------|
| **Revenue (total)** | OLAP SALES: `DishSumInt` | v2 OLAP | Sum of all non-deleted orders |
| **Revenue (delivery)** | OLAP SALES: `DishSumInt` where `OrderType` in delivery types | v2 OLAP | Filter by OrderType |
| **Revenue (hall)** | OLAP SALES: `DishSumInt` where `OrderType` in hall types | v2 OLAP | Filter by OrderType |
| **Labor cost** | Attendance: `regularPayedMinutes` + `staff_rates.hourly_rate` | v1 XML + local DB | Join attendance hours with hourly rates |
| **Write-offs** | OLAP TRANSACTIONS or manual entry | v2 OLAP or manual | Need to determine exact OLAP fields |

### KPF Formulas

```
LC% = (labor_cost_total / revenue_total) * 100
KC% = (writeoff_total / revenue_total) * 100
KPF = f(LC%, KC%, ...)  -- exact formula TBD per business requirements
```

### Labor Cost Calculation

```sql
-- Join attendance with SCD Type 2 staff rates
SELECT
  a.employee_id,
  a.employee_name,
  a.worked_hours,
  r.hourly_rate,
  a.worked_hours * r.hourly_rate AS labor_cost
FROM employee_attendance a
JOIN staff_rates r ON r.employee_id = a.employee_id
  AND r.valid_from <= a.date_from::date
  AND (r.valid_to > a.date_from::date OR r.valid_to IS NULL)
WHERE a.branch_id = :branch_id
  AND a.date_from >= :date_from
  AND a.date_from < :date_to
```

### Available iiko-Computed Pay

If `withPaymentDetails=true` in the attendance API, iiko returns pre-computed pay:
- `regularPaymentSum` - regular pay (based on iiko's internal rate)
- `overtimePayedSum` - overtime pay
- `otherPaymentsSum` - other payments

**Note:** For hourly employees, iiko computes this automatically. For salaried employees, `paymentDetails` is **empty** - their labor cost must be calculated separately using the salary API.

### Recommended Approach

1. **Primary**: Use iiko's `paymentDetails.regularPaymentSum` from attendance API when available
2. **Fallback**: For salaried employees or when iiko rates differ from actual, use local `staff_rates` table
3. **Override**: Allow manual hourly rate entry via admin endpoint for employees whose iiko salary doesn't reflect actual labor cost

---

## Appendix: Demo Instance Details

```
Domain: 571-709-897
Account ID: 108025
Store ID: 156199
Department ID: 4549c2da-bd1c-ad76-0199-18a5f17b0012
iiko Version: 9.6.2.248843
Restaurant Name: Мой ресторан
Web UI: https://571-709-897.iikoweb.ru
RMS API: https://571-709-897.iiko.it (internal DNS - may not resolve publicly)
Login: user
Password: user#test
```

**Note:** The `.iiko.it` domain resolves only within iiko's internal network. The `.iikoweb.ru` domain is the web UI frontend with a separate JWT-based API (not the REST API documented above). The demo RMS server was offline (`isAliveConnection: false`) during initial testing.
