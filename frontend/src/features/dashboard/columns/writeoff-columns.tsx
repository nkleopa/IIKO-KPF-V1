import type { ColumnDef } from "@tanstack/react-table";
import type { WriteoffRow } from "@/lib/api";
import { Badge } from "@/components/ui/badge";

const fmtRub = (v: number) =>
  new Intl.NumberFormat("ru-RU", { style: "currency", currency: "RUB", maximumFractionDigits: 0 }).format(v);

const categoryLabel: Record<string, string> = {
  spoilage: "Бракераж/Порча",
  marketing: "Маркетинг",
  promo: "Акции/Подарки",
  staff_meals: "Питание персонала",
  dish_removal: "Удаление блюд",
  beer_drain: "Слив пива",
  consumables: "Расходники",
  r_and_d: "Проработка",
  cogs: "Себестоимость",
  founders_meals: "Представительские",
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
    accessorKey: "account_name",
    header: "Статья списания",
    cell: ({ row }) => row.getValue<string | null>("account_name") ?? "—",
  },
  {
    accessorKey: "product_name",
    header: "Продукт",
    cell: ({ row }) => row.getValue<string | null>("product_name") ?? "—",
  },
  {
    accessorKey: "item_quantity",
    header: "Кол-во",
    cell: ({ row }) => {
      const v = row.getValue<number | null>("item_quantity");
      return v != null ? Number(v).toFixed(1) : "—";
    },
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
