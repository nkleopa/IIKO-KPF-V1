import type { ColumnDef } from "@tanstack/react-table";
import type { LaborRow } from "@/lib/api";

const fmtRub = (v: number) =>
  new Intl.NumberFormat("ru-RU", { style: "currency", currency: "RUB", maximumFractionDigits: 0 }).format(v);

export const laborColumns: ColumnDef<LaborRow>[] = [
  {
    accessorKey: "employee_name",
    header: "Сотрудник",
  },
  {
    accessorKey: "role_name",
    header: "Должность",
    cell: ({ row }) => row.getValue<string | null>("role_name") ?? "—",
  },
  {
    accessorKey: "total_hours",
    header: "Часы",
    cell: ({ row }) => Number(row.getValue<number>("total_hours")).toFixed(1),
  },
  {
    accessorKey: "hourly_rate",
    header: "Ставка (₽/ч)",
    cell: ({ row }) => fmtRub(row.getValue<number>("hourly_rate")),
  },
  {
    accessorKey: "labor_cost",
    header: "Стоимость труда",
    cell: ({ row }) => fmtRub(row.getValue<number>("labor_cost")),
  },
];
