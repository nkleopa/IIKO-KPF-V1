import { DataTable } from "@/components/data-table/data-table";
import { revenueColumns } from "../columns/revenue-columns";
import type { RevenueRow } from "@/lib/api";

interface Props {
  data: RevenueRow[] | undefined;
  isLoading: boolean;
}

export function RevenueTable({ data, isLoading }: Props) {
  if (isLoading) {
    return <div className="h-48 flex items-center justify-center text-muted-foreground">Загрузка...</div>;
  }
  return <DataTable columns={revenueColumns} data={data ?? []} />;
}
