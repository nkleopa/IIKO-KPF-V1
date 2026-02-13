import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { KPFData } from "@/lib/api";

const fmtRub = (v: number) =>
  new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "RUB",
    maximumFractionDigits: 0,
  }).format(v);

const fmtQty = (v: number) =>
  new Intl.NumberFormat("ru-RU", { maximumFractionDigits: 0 }).format(v);

interface KPFCardsProps {
  data: KPFData | undefined;
  isLoading: boolean;
}

interface MetricCardProps {
  title: string;
  value: string;
  subtitle?: string;
}

function MetricCard({ title, value, subtitle }: MetricCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {subtitle && (
          <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>
        )}
      </CardContent>
    </Card>
  );
}

export function KPFCards({ data, isLoading }: KPFCardsProps) {
  if (isLoading || !data) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i}>
            <CardHeader className="pb-2">
              <div className="h-4 w-24 bg-muted rounded animate-pulse" />
            </CardHeader>
            <CardContent>
              <div className="h-8 w-32 bg-muted rounded animate-pulse" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          title="Выручка (итого)"
          value={fmtRub(data.revenue_total)}
          subtitle={`Зал: ${fmtRub(data.revenue_hall)}`}
        />
        <MetricCard
          title="Доставка"
          value={fmtRub(data.revenue_delivery)}
        />
        <MetricCard
          title="LC %"
          value={`${data.lc_percent}%`}
          subtitle={`Зал: ${fmtRub(data.hall_labor_cost)} | Кухня: ${fmtRub(data.kitchen_labor_cost)}`}
        />
        <MetricCard
          title="KC %"
          value={`${data.kc_percent}%`}
          subtitle={`Кухня: ${fmtRub(data.kitchen_labor_cost)}`}
        />
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          title="Списания"
          value={fmtRub(data.writeoff_total)}
        />
        <MetricCard
          title="Хинкали (шт)"
          value={fmtQty(data.khinkali_count)}
        />
        {data.upsells && (
          <>
            <MetricCard
              title="Узвар (шт)"
              value={fmtQty(data.upsells.uzvar_qty)}
            />
            <MetricCard
              title="Соусы (шт)"
              value={fmtQty(data.upsells.sauce_qty)}
            />
            <MetricCard
              title="Хлеб шотис-пури (шт)"
              value={fmtQty(data.upsells.bread_qty)}
            />
          </>
        )}
      </div>
    </div>
  );
}
