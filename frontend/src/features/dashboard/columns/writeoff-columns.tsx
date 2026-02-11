import type { ColumnDef } from "@tanstack/react-table";
import type { WriteoffRow } from "@/lib/api";
import { Badge } from "@/components/ui/badge";

const fmtRub = (v: number) =>
  new Intl.NumberFormat("ru-RU", { style: "currency", currency: "RUB", maximumFractionDigits: 0 }).format(v);

const categoryLabel: Record<string, string> = {
  spoilage: "Бракераж",
  marketing: "Маркетинг",
  other: "Прочее",
};

export const writeoffColumns: ColumnDef<WriteoffRow>[] = [
  {
    accessorKey: "date",
    header: "Дата",
    cell: ({ row }) => {
      const d = new Date(row.getValue<string>("date"));
      return d.toLocaleDateString("ru-RU");
    },
  },
  {
    accessorKey: "article_name",
    header: "Статья",
  },
  {
    accessorKey: "category",
    header: "Категория",
    cell: ({ row }) => {
      const cat = row.getValue<string>("category");
      return <Badge variant="outline">{categoryLabel[cat] ?? cat}</Badge>;
    },
  },
  {
    accessorKey: "amount",
    header: "Сумма",
    cell: ({ row }) => fmtRub(row.getValue<number>("amount")),
  },
];
