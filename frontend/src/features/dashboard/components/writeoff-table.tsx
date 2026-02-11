import { DataTable } from "@/components/data-table/data-table";
import { writeoffColumns } from "../columns/writeoff-columns";
import type { WriteoffRow } from "@/lib/api";

interface Props {
  data: WriteoffRow[] | undefined;
  isLoading: boolean;
}

export function WriteoffTable({ data, isLoading }: Props) {
  if (isLoading) {
    return <div className="h-48 flex items-center justify-center text-muted-foreground">Загрузка...</div>;
  }
  return <DataTable columns={writeoffColumns} data={data ?? []} />;
}
