import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

interface Params {
  branch_id: number;
  date_from: string;
  date_to: string;
  [key: string]: string | number;
}

export function useWaiterChecks(params: Params) {
  return useQuery({
    queryKey: ["waiterChecks", params],
    queryFn: () => api.getWaiterChecks(params),
    enabled: params.branch_id > 0,
  });
}

export function useSyncWaiterChecks() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ dateFrom, dateTo }: { dateFrom: string; dateTo: string }) =>
      api.syncWaiterChecks(dateFrom, dateTo),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["waiterChecks"] });
      queryClient.invalidateQueries({ queryKey: ["branches"] });
      queryClient.invalidateQueries({ queryKey: ["dishCategories"] });
    },
  });
}
