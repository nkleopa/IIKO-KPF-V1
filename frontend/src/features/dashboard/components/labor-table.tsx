import { DataTable } from "@/components/data-table/data-table";
import { laborColumns } from "../columns/labor-columns";
import type { LaborRow } from "@/lib/api";

interface Props {
  data: LaborRow[] | undefined;
  isLoading: boolean;
}

export function LaborTable({ data, isLoading }: Props) {
  if (isLoading) {
    return <div className="h-48 flex items-center justify-center text-muted-foreground">Загрузка...</div>;
  }
  return <DataTable columns={laborColumns} data={data ?? []} />;
}
