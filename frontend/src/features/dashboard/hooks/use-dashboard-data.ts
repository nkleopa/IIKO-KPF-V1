import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

interface Params {
  branch_id: number;
  date_from: string;
  date_to: string;
  [key: string]: string | number;
}

export function useKPF(params: Params) {
  return useQuery({
    queryKey: ["kpf", params],
    queryFn: () => api.getKPF(params),
  });
}

export function useRevenue(params: Params) {
  return useQuery({
    queryKey: ["revenue", params],
    queryFn: () => api.getRevenue(params),
  });
}

export function useLabor(params: Params) {
  return useQuery({
    queryKey: ["labor", params],
    queryFn: () => api.getLabor(params),
  });
}

export function useWriteoffs(params: Params) {
  return useQuery({
    queryKey: ["writeoffs", params],
    queryFn: () => api.getWriteoffs(params),
  });
}

export function useSyncStatus() {
  return useQuery({
    queryKey: ["syncStatus"],
    queryFn: () => api.getSyncStatus(),
    refetchInterval: 10_000,
  });
}

export function useBranches() {
  return useQuery({
    queryKey: ["branches"],
    queryFn: () => api.getBranches(),
  });
}
