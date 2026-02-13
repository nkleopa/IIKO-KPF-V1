import { useMemo } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { LaborRow } from "@/lib/api";

const fmtRub = (v: number) =>
  new Intl.NumberFormat("ru-RU", { style: "currency", currency: "RUB", maximumFractionDigits: 0 }).format(v);

const groupLabel: Record<string, string> = {
  kitchen: "Кухня",
  hall: "Зал",
  other: "Прочее",
};

const groupOrder = ["kitchen", "hall", "other"] as const;

interface Props {
  data: LaborRow[] | undefined;
  isLoading: boolean;
}

export function LaborTable({ data, isLoading }: Props) {
  const grouped = useMemo(() => {
    if (!data) return [];
    const groups: Record<string, LaborRow[]> = {};
    for (const row of data) {
      const g = row.group || "other";
      if (!groups[g]) groups[g] = [];
      groups[g].push(row);
    }
    return groupOrder
      .filter((g) => groups[g]?.length)
      .map((g) => ({
        key: g,
        label: groupLabel[g] ?? g,
        rows: groups[g],
        totalHours: groups[g].reduce((s, r) => s + Number(r.total_hours), 0),
        totalCost: groups[g].reduce((s, r) => s + Number(r.labor_cost), 0),
      }));
  }, [data]);

  if (isLoading) {
    return <div className="h-48 flex items-center justify-center text-muted-foreground">Загрузка...</div>;
  }

  if (!data?.length) {
    return <div className="h-24 flex items-center justify-center text-muted-foreground">Нет данных</div>;
  }

  const grandTotalHours = grouped.reduce((s, g) => s + g.totalHours, 0);
  const grandTotalCost = grouped.reduce((s, g) => s + g.totalCost, 0);

  return (
    <div className="rounded-md border bg-white">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Сотрудник</TableHead>
            <TableHead>Должность</TableHead>
            <TableHead className="text-right">Часы</TableHead>
            <TableHead className="text-right">Ставка (₽/ч)</TableHead>
            <TableHead className="text-right">Стоимость труда</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {grouped.map((group) => (
            <>
              <TableRow key={`hdr-${group.key}`} className="bg-muted/50">
                <TableCell colSpan={5} className="font-semibold">
                  {group.label}
                </TableCell>
              </TableRow>
              {group.rows.map((row, i) => (
                <TableRow key={`${group.key}-${i}`}>
                  <TableCell>{row.employee_name}</TableCell>
                  <TableCell className="text-muted-foreground">{row.role_name ?? "—"}</TableCell>
                  <TableCell className="text-right">{Number(row.total_hours).toFixed(1)}</TableCell>
                  <TableCell className="text-right">{fmtRub(row.hourly_rate)}</TableCell>
                  <TableCell className="text-right">{fmtRub(row.labor_cost)}</TableCell>
                </TableRow>
              ))}
              <TableRow key={`sub-${group.key}`} className="bg-muted/30 font-medium">
                <TableCell colSpan={2} className="text-right">
                  Итого {group.label.toLowerCase()}:
                </TableCell>
                <TableCell className="text-right">{group.totalHours.toFixed(1)}</TableCell>
                <TableCell />
                <TableCell className="text-right">{fmtRub(group.totalCost)}</TableCell>
              </TableRow>
            </>
          ))}
          <TableRow className="bg-muted font-bold">
            <TableCell colSpan={2} className="text-right">
              Итого:
            </TableCell>
            <TableCell className="text-right">{grandTotalHours.toFixed(1)}</TableCell>
            <TableCell />
            <TableCell className="text-right">{fmtRub(grandTotalCost)}</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>
  );
}
