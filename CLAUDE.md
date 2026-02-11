# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

iiko KPF Dashboard — a full-stack SaaS application for calculating restaurant Branch Performance Coefficient (KPF) metrics. It fetches data **read-only** from the iiko ERP API, caches it in PostgreSQL, and presents analytics via a React dashboard.

**Current phase**: Alpha — single branch "СХ Воронеж-Пушкинская". Next: scale to 14 branches, then multi-tenant SaaS.

## Commands

### Run everything (Docker)
```bash
docker compose up --build
```
Services: `postgres:5433`, `backend:8000`, `frontend:5173`

### Frontend (from `frontend/`)
```bash
npm run dev          # Vite dev server at :5173
npm run build        # TypeScript check + Vite production build
npm run preview      # Preview production build
```

### Backend (from `backend/`)
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Database migrations (from `backend/`)
```bash
alembic upgrade head          # Apply all migrations
alembic revision --autogenerate -m "description"  # Create new migration
```

## Architecture

### Backend: FastAPI + async SQLAlchemy
- **`backend/app/main.py`** — App entry, CORS, lifespan (scheduler startup), route mounting
- **`backend/app/core/config.py`** — Pydantic Settings from `.env` (IIKO_HOST, IIKO_LOGIN, IIKO_PASSWORD, DATABASE_URL, SYNC_HOUR/MINUTE)
- **`backend/app/api/v1/`** — REST endpoints: dashboard/kpf, revenue, labor, writeoffs, sync, branches. All accept `branch_id`, `date_from`, `date_to` query params
- **`backend/app/services/`** — Business logic: revenue aggregation, labor cost calculation, write-off mapping, KPF formula
- **`backend/app/worker/`** — APScheduler CronTrigger for daily sync at 03:00 AM
- **`backend/app/models/`** — SQLAlchemy models: Branch, DailyRevenue, EmployeeAttendance, StaffRate (SCD Type 2), Writeoff, SyncLog
- **`backend/alembic/`** — Database migrations (async PostgreSQL via asyncpg)

### Frontend: React + Vite + shadcn/ui
- **`frontend/src/features/dashboard/`** — Main feature: page.tsx (layout/state), components/ (tables), hooks/ (React Query), columns/ (TanStack Table definitions)
- **`frontend/src/components/ui/`** — shadcn/ui components (New York style, Radix primitives)
- **`frontend/src/components/layout/`** — Header, DashboardShell
- **`frontend/src/components/data-table/`** — Generic reusable data table
- **`frontend/src/lib/api.ts`** — API client with TypeScript interfaces and `fetchJSON()` helper
- **`frontend/src/hooks/`** — Shared hooks (date range)
- Path alias: `@/*` → `./src/*`
- Vite proxies `/api/*` → `http://backend:8000` (Docker network)

### Data flow
1. APScheduler triggers daily sync → backend fetches from iiko API (OLAP reports as JSON, attendance as XML)
2. Data stored in PostgreSQL (local cache)
3. Frontend queries backend REST API via React Query (TanStack Query v5)
4. Dashboard renders KPF metrics, revenue/labor/writeoff tables with TanStack Table v8

## Key Business Rules (KPF Manual Calibration)

- **Revenue**: Use "Revenue with discount" (Сумма со скидкой) from OLAP Report "02".
- **Order Mapping** (iiko OLAP `OrderType` field values):
    - **Delivery**: "ДОСТАВКА" (also accept "Яндекс", "Бронибой", "Личная курьерская доставка" if they appear as sub-types).
    - **Hall**: "ОБЫЧНЫЙ ЗАКАЗ", "Самовывоз".
    - **Excluded** from KPF revenue: "ПРЕДЗАКАЗ", "С СОБОЙ (СС)", and any other types.
- **KPF Formulas**:
    - `KC% = (Kitchen_Labor_Cost / Total_Revenue) × 100`
    - `LC% = (Total_Labor_Cost / Total_Revenue) × 100`
- **Labor Rules**:
    - Use "Duration" (Продолжительность) = `dateTo - dateFrom` from Attendance Journal XML (the API has no `duration` field; calculate from timestamps).
    - **CRITICAL EXCLUSION**: Do NOT include hours for roles containing "Управляющий" (Manager) or "Су-шеф" (Sous-chef) in hourly labor calculations. Use **substring matching** — iiko role names have suffixes (e.g. "Управляющий / Бухгалтер СВОБ").
    - **Kitchen roles** (for KC%): roles containing "Повар" or "Мангал" (e.g. "Повар СВОБ", "Повар Хинкали РАСП", "Повар Мангал СВОБ").
- **Khinkali Rule**: If item name contains "Дюжина Хинкали", multiply quantity by 12.
- **Staff rates**: SCD Type 2 history in PostgreSQL — hourly rates change over time, old records preserved.
- **STRICT READ-ONLY**: Never write to iiko. Only fetch and cache locally. Daily sync at 03:00 AM.

## iiko API Integration (Discovered Specs)

- **Auth**: POST to `/resto/api/auth` with `SHA1(password)` hash (No "resto#" prefix needed for this server).
- **Format**: Use Form-encoded POST body for auth and logout.
- **Session**: Always POST to `/resto/api/logout` to free up the single available license slot.
- **Endpoints**:
    - OLAP (Revenue/Upsells): `/resto/api/v2/reports/olap` (JSON).
    - Attendance: `/resto/api/employees/attendance` (XML). No `duration` field in response; calculate from `dateFrom`/`dateTo` timestamps. Use `withPaymentDetails=true` for payment sums.
    - COGS: Pull from P&L report as "% of revenue".
- Reference docs: `IIKO_KNOWLEDGE_BASE.md` and `IIKO_MASTER_REFERENCE.md` in repo root.

## Environment Variables

Defined in `.env` (see `.env.example`): `IIKO_HOST`, `IIKO_LOGIN`, `IIKO_PASSWORD`, `DATABASE_URL`, `SYNC_HOUR`, `SYNC_MINUTE`

## UI Language

All user-facing labels, table headers (Выручка, Труд, Списания), and metrics are in **Russian**. Maintain this convention.
