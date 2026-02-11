import type { ColumnDef } from "@tanstack/react-table";
import type { RevenueRow } from "@/lib/api";
import { Badge } from "@/components/ui/badge";

const fmtRub = (v: number) =>
  new Intl.NumberFormat("ru-RU", { style: "currency", currency: "RUB", maximumFractionDigits: 0 }).format(v);

export const revenueColumns: ColumnDef<RevenueRow>[] = [
  {
    accessorKey: "date",
    header: "Дата",
    cell: ({ row }) => {
      const d = new Date(row.getValue<string>("date"));
      return d.toLocaleDateString("ru-RU");
    },
  },
  {
    accessorKey: "order_type",
    header: "Тип",
    cell: ({ row }) => {
      const t = row.getValue<string>("order_type");
      return (
        <Badge variant={t === "delivery" ? "default" : t === "hall" ? "secondary" : "outline"}>
          {t === "delivery" ? "Доставка" : t === "hall" ? "Зал" : t}
        </Badge>
      );
    },
  },
  {
    accessorKey: "order_type_detail",
    header: "Тип (iiko)",
  },
  {
    accessorKey: "item_name",
    header: "Блюдо",
  },
  {
    accessorKey: "revenue_amount",
    header: "Выручка",
    cell: ({ row }) => fmtRub(row.getValue<number>("revenue_amount")),
  },
  {
    accessorKey: "order_count",
    header: "Кол-во",
  },
];
