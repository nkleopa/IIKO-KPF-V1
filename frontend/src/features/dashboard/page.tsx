import { useState } from "react";
import { format } from "date-fns";
import { CheckCircle2, XCircle, Loader2 } from "lucide-react";

import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Header } from "@/components/layout/header";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { useDateRange } from "@/hooks/use-date-range";
import {
  useBranches,
  useKPF,
  useLabor,
  useRevenue,
  useSyncStatus,
  useWriteoffs,
} from "./hooks/use-dashboard-data";
import { KPFCards } from "./components/kpf-cards";
import { RevenueTable } from "./components/revenue-table";
import { LaborTable } from "./components/labor-table";
import { WriteoffTable } from "./components/writeoff-table";

export function DashboardPage() {
  const [branchId, setBranchId] = useState(2);
  const { dateFrom, dateTo, setDateFrom, setDateTo, dateFromStr, dateToStr } =
    useDateRange();

  const params = { branch_id: branchId, date_from: dateFromStr, date_to: dateToStr };

  const { data: branches } = useBranches();
  const { data: kpf, isLoading: kpfLoading } = useKPF(params);
  const { data: revenue, isLoading: revLoading } = useRevenue(params);
  const { data: labor, isLoading: laborLoading } = useLabor(params);
  const { data: writeoffs, isLoading: woLoading } = useWriteoffs(params);
  const { data: syncStatus } = useSyncStatus();

  return (
    <DashboardShell>
      <Header
        branches={branches ?? [{ id: 1, name: "СХ Воронеж-Пушкинская", city: "Воронеж", territory: null, is_active: true }]}
        selectedBranchId={branchId}
        onBranchChange={setBranchId}
        dateFrom={dateFrom}
        dateTo={dateTo}
        onDateFromChange={setDateFrom}
        onDateToChange={setDateTo}
      />

      <main className="p-6 space-y-6">
        <KPFCards data={kpf} isLoading={kpfLoading} />

        <Separator />

        <Tabs defaultValue="revenue" className="space-y-4">
          <TabsList>
            <TabsTrigger value="revenue">Выручка</TabsTrigger>
            <TabsTrigger value="labor">Труд</TabsTrigger>
            <TabsTrigger value="writeoffs">Списания</TabsTrigger>
          </TabsList>
          <TabsContent value="revenue">
            <RevenueTable data={revenue} isLoading={revLoading} />
          </TabsContent>
          <TabsContent value="labor">
            <LaborTable data={labor} isLoading={laborLoading} />
          </TabsContent>
          <TabsContent value="writeoffs">
            <WriteoffTable data={writeoffs} isLoading={woLoading} />
          </TabsContent>
        </Tabs>

        {syncStatus && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground pt-4">
            {syncStatus.status === "success" ? (
              <CheckCircle2 className="h-4 w-4 text-green-500" />
            ) : syncStatus.status === "failed" ? (
              <XCircle className="h-4 w-4 text-red-500" />
            ) : (
              <Loader2 className="h-4 w-4 animate-spin" />
            )}
            <span>
              Синхронизация: {syncStatus.completed_at
                ? format(new Date(syncStatus.completed_at), "dd.MM.yyyy HH:mm")
                : "в процессе"}
            </span>
            <span>—</span>
            <span>
              {syncStatus.status === "success"
                ? "Успешно"
                : syncStatus.status === "failed"
                  ? "Ошибка"
                  : "Выполняется"}
            </span>
          </div>
        )}
      </main>
    </DashboardShell>
  );
}
