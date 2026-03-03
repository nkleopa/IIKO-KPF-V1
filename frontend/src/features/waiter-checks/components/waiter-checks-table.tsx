import { Fragment, useMemo } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { WaiterCheckRow } from "@/lib/api";

const fmtRub = (v: number) =>
  new Intl.NumberFormat("ru-RU", { style: "currency", currency: "RUB", maximumFractionDigits: 0 }).format(v);

const fmtDate = (d: string) => {
  const [y, m, day] = d.split("-");
  return `${day}.${m}.${y}`;
};

const fmtFullness = (v: number | null) => (v != null ? Number(v).toFixed(1) : "—");
const fmtPct = (v: number | null) => (v != null ? `${Number(v).toFixed(1)}%` : "—");

/** Weighted average of fullness/pct_ideal across rows, weighted by check_count. */
function weightedAvg(rows: WaiterCheckRow[], field: "avg_fullness" | "pct_ideal"): number | null {
  let totalWeight = 0;
  let totalValue = 0;
  for (const r of rows) {
    const v = r[field];
    if (v != null) {
      totalWeight += r.check_count;
      totalValue += Number(v) * r.check_count;
    }
  }
  return totalWeight > 0 ? totalValue / totalWeight : null;
}

interface Props {
  data: WaiterCheckRow[] | undefined;
  isLoading: boolean;
}

export function WaiterChecksTable({ data, isLoading }: Props) {
  const grouped = useMemo(() => {
    if (!data) return [];
    const groups: Record<string, WaiterCheckRow[]> = {};
    for (const row of data) {
      if (!groups[row.date]) groups[row.date] = [];
      groups[row.date].push(row);
    }
    return Object.keys(groups)
      .sort()
      .map((date) => ({
        date,
        rows: groups[date].sort((a, b) => a.waiter_name.localeCompare(b.waiter_name, "ru")),
        totalChecks: groups[date].reduce((s, r) => s + r.check_count, 0),
        totalRevenue: groups[date].reduce((s, r) => s + Number(r.revenue), 0),
        avgFullness: weightedAvg(groups[date], "avg_fullness"),
        pctIdeal: weightedAvg(groups[date], "pct_ideal"),
      }));
  }, [data]);

  if (isLoading) {
    return <div className="h-48 flex items-center justify-center text-muted-foreground">Загрузка...</div>;
  }

  if (!data?.length) {
    return <div className="h-24 flex items-center justify-center text-muted-foreground">Нет данных</div>;
  }

  const grandTotalChecks = grouped.reduce((s, g) => s + g.totalChecks, 0);
  const grandTotalRevenue = grouped.reduce((s, g) => s + g.totalRevenue, 0);
  const grandAvgFullness = weightedAvg(data, "avg_fullness");
  const grandPctIdeal = weightedAvg(data, "pct_ideal");

  return (
    <div className="rounded-md border bg-white">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Дата</TableHead>
            <TableHead>Официант</TableHead>
            <TableHead className="text-right">Кол-во чеков</TableHead>
            <TableHead className="text-right">Выручка</TableHead>
            <TableHead className="text-right">Средний чек</TableHead>
            <TableHead className="text-right">Ср. наполн.</TableHead>
            <TableHead className="text-right">% идеал.</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {grouped.map((group) => (
            <Fragment key={group.date}>
              <TableRow className="bg-muted/50">
                <TableCell colSpan={7} className="font-semibold">
                  {fmtDate(group.date)}
                </TableCell>
              </TableRow>
              {group.rows.map((row, i) => (
                <TableRow key={`${group.date}-${i}`}>
                  <TableCell />
                  <TableCell>{row.waiter_name}</TableCell>
                  <TableCell className="text-right">{row.check_count}</TableCell>
                  <TableCell className="text-right">{fmtRub(Number(row.revenue))}</TableCell>
                  <TableCell className="text-right">{fmtRub(Number(row.avg_check))}</TableCell>
                  <TableCell className="text-right">{fmtFullness(row.avg_fullness)}</TableCell>
                  <TableCell className="text-right">{fmtPct(row.pct_ideal)}</TableCell>
                </TableRow>
              ))}
              <TableRow className="bg-muted/30 font-medium">
                <TableCell colSpan={2} className="text-right">
                  Итого за {fmtDate(group.date)}:
                </TableCell>
                <TableCell className="text-right">{group.totalChecks}</TableCell>
                <TableCell className="text-right">{fmtRub(group.totalRevenue)}</TableCell>
                <TableCell className="text-right">
                  {group.totalChecks > 0 ? fmtRub(group.totalRevenue / group.totalChecks) : "—"}
                </TableCell>
                <TableCell className="text-right">{fmtFullness(group.avgFullness)}</TableCell>
                <TableCell className="text-right">{fmtPct(group.pctIdeal)}</TableCell>
              </TableRow>
            </Fragment>
          ))}
          <TableRow className="bg-muted font-bold">
            <TableCell colSpan={2} className="text-right">
              Итого:
            </TableCell>
            <TableCell className="text-right">{grandTotalChecks}</TableCell>
            <TableCell className="text-right">{fmtRub(grandTotalRevenue)}</TableCell>
            <TableCell className="text-right">
              {grandTotalChecks > 0 ? fmtRub(grandTotalRevenue / grandTotalChecks) : "—"}
            </TableCell>
            <TableCell className="text-right">{fmtFullness(grandAvgFullness)}</TableCell>
            <TableCell className="text-right">{fmtPct(grandPctIdeal)}</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>
  );
}
