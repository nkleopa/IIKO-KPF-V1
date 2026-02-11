# Product Requirements Document: iiko KPF Dashboard (SaaS)

## 1. Product Vision & Business Goal
- **The Problem**: Restaurant owners in the iiko ecosystem lack a streamlined, automated way to calculate the "Branch Performance Coefficient" (KPF) without manual spreadsheet work or risking live DB integrity.
- **The Mission**: Build a scalable, modern Dashboard that transforms raw ERP data into actionable business insights.
- **Roadmap**:
    1. **Alpha**: Perfect the logic for one specific branch ("СХ Воронеж-Пушкинская").
    2. **Internal Beta**: Scale to 14 branches with city/territory grouping and global aggregates.
    3. **SaaS MVP**: Prepare architecture for multi-tenancy to sell this as a service to other restaurant owners.

## 2. Human-Centric UI/UX Goals
- **Design**: Minimalist, high-performance, professional (SaaS-grade UI).
- **Usability**: Fast navigation between branches, clear visual indicators for KC% and LC% metrics.
- **Validation**: Use **playwright mcp** to verify the interface looks like a premium product and ensure no UI regressions.

## 3. Technical Strategy
- **Discovery Phase**: 
    - **MUST USE playwright mcp** to navigate and browse: https://ru.iiko.help/articles/#!api-documentations/iikoserver-api.
    - Identify exact endpoints for Login, OLAP Reports, and Attendance.
    - Use **context7 mcp** for technical lookups of frameworks (FastAPI, React, shadcn/ui).
- **Infrastructure**: FastAPI (Backend), PostgreSQL (SCD Type 2 for staff rates history), React + shadcn/ui (Frontend).
- **Data Safety**: **STRICT READ-ONLY**. Data must be fetched once a day at 03:00 AM and cached locally. No direct writes to iiko.
- **Environment**:
    - Host: `starikhinkalich-co.iiko.it`
    - Login: `KPFKleopa`
    - Pass: `KPFKleopa12345`

## 4. Data Mapping Logic (ETL)
- **Revenue**: Group `OrderType` (Delivery vs Hall) from OLAP "02 Отчет по выручке СХ".
    - *Delivery*: "Доставка Хинк...", "Доставка курьер", "Яндекс.Еда", "Бронибой".
    - *Hall*: "Обычный заказ", "С собой (СС)", "Самовывоз".
- **Labor Cost**: Aggregate Attendance hours from iiko and multiply by historical hourly rates stored in local PostgreSQL.
- **Write-offs**: Map specific articles (e.g., "Бракераж", "2.10.1 Маркетинг") to local categories.
- **Special Rule**: If item name contains "Дюжина Хинкали", apply x12 multiplier to the quantity.

## 5. Deliverables
- Fully containerized application (Docker Compose) ready for NetCap hosting.
- Background synchronization engine running daily at 03:00 AM.
- Clean, interactive UI with branch switching and date filtering.

## 6. Development Instructions for the Agent
1. **Start by using Playwright MCP** to explore the iiko documentation at the provided URL. Locate the "iikoServer API" specifications.
2. Initialize the project structure (Backend/Frontend/DB).
3. Create a `.env` file with the provided credentials.
4. Draft the SQLAlchemy model for `staff_rates` to handle historical rate changes.
5. Implement a "Zero-Hallucination" policy: if the API schema differs from this PRD, report it immediately instead of assuming.