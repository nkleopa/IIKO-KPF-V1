import { useState } from "react";
import { Loader2, RefreshCw } from "lucide-react";

import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Header } from "@/components/layout/header";
import { Button } from "@/components/ui/button";
import { useDateRange } from "@/hooks/use-date-range";
import { useBranches } from "@/features/dashboard/hooks/use-dashboard-data";
import { useWaiterChecks, useSyncWaiterChecks } from "./hooks/use-waiter-checks";
import { WaiterChecksTable } from "./components/waiter-checks-table";

export function WaiterChecksPage() {
  const [branchId, setBranchId] = useState(0); // 0 = not selected yet
  const { dateFrom, dateTo, setDateFrom, setDateTo, dateFromStr, dateToStr } =
    useDateRange();

  const { data: branches } = useBranches();
  const rostovBranches = (branches ?? []).filter((b) =>
    b.name.includes("Ростов")
  );

  // Auto-select first Rostov branch if none selected
  const effectiveBranchId = branchId || rostovBranches[0]?.id || 0;

  const params = {
    branch_id: effectiveBranchId,
    date_from: dateFromStr,
    date_to: dateToStr,
  };

  const { data, isLoading } = useWaiterChecks(
    effectiveBranchId ? params : { branch_id: 0, date_from: "", date_to: "" }
  );

  const syncMutation = useSyncWaiterChecks();

  const handleSync = () => {
    syncMutation.mutate({ dateFrom: dateFromStr, dateTo: dateToStr });
  };

  return (
    <DashboardShell>
      <Header
        branches={rostovBranches}
        selectedBranchId={effectiveBranchId}
        onBranchChange={setBranchId}
        dateFrom={dateFrom}
        dateTo={dateTo}
        onDateFromChange={setDateFrom}
        onDateToChange={setDateTo}
      />

      <main className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Чеки официантов</h2>
          <Button
            onClick={handleSync}
            disabled={syncMutation.isPending}
            variant="outline"
          >
            {syncMutation.isPending ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="mr-2 h-4 w-4" />
            )}
            Синхронизировать
          </Button>
        </div>

        {syncMutation.isSuccess && (
          <div className="text-sm text-green-600">
            {syncMutation.data?.message}
          </div>
        )}
        {syncMutation.isError && (
          <div className="text-sm text-red-600">
            Ошибка синхронизации
          </div>
        )}

        {!effectiveBranchId ? (
          <div className="h-24 flex items-center justify-center text-muted-foreground">
            Сначала синхронизируйте данные — нажмите "Синхронизировать"
          </div>
        ) : (
          <WaiterChecksTable data={data} isLoading={isLoading} />
        )}
      </main>
    </DashboardShell>
  );
}
