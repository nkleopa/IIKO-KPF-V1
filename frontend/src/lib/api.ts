const BASE = "/api/v1";

async function fetchJSON<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

function qs(params: { [key: string]: string | number }) {
  const entries: [string, string][] = [];
  for (const key in params) {
    entries.push([key, String(params[key])]);
  }
  return new URLSearchParams(entries).toString();
}

// --- Types ---

export interface UpsellData {
  uzvar_qty: number;
  sauce_qty: number;
  bread_qty: number;
}

export interface KPFData {
  revenue_total: number;
  revenue_delivery: number;
  revenue_hall: number;
  labor_cost_total: number;
  kitchen_labor_cost: number;
  writeoff_total: number;
  lc_percent: number;
  kc_percent: number;
  khinkali_count: number;
  upsells: UpsellData | null;
  cogs_percent: number | null;
}

export interface RevenueRow {
  date: string;
  order_type: string;
  order_type_detail: string;
  revenue_amount: number;
  order_count: number;
  item_name: string | null;
  item_quantity: number | null;
  item_quantity_adjusted: number | null;
}

export interface LaborRow {
  employee_name: string;
  role_name: string | null;
  total_hours: number;
  hourly_rate: number;
  labor_cost: number;
}

export interface WriteoffRow {
  date: string;
  article_name: string;
  category: string;
  amount: number;
}

export interface WriteoffSummaryRow {
  category: string;
  total_amount: number;
}

export interface SyncStatus {
  batch_id: string;
  sync_type: string;
  status: string;
  records_processed: number;
  error_message: string | null;
  started_at: string;
  completed_at: string | null;
}

export interface BranchInfo {
  id: number;
  name: string;
  city: string | null;
  territory: string | null;
  is_active: boolean;
}

// --- API calls ---

interface DateRange {
  [key: string]: string | number;
  branch_id: number;
  date_from: string;
  date_to: string;
}

export const api = {
  getKPF: (p: DateRange) =>
    fetchJSON<KPFData>(`${BASE}/dashboard/kpf?${qs(p)}`),

  getRevenue: (p: DateRange) =>
    fetchJSON<RevenueRow[]>(`${BASE}/revenue?${qs(p)}`),

  getLabor: (p: DateRange) =>
    fetchJSON<LaborRow[]>(`${BASE}/labor?${qs(p)}`),

  getWriteoffs: (p: DateRange) =>
    fetchJSON<WriteoffRow[]>(`${BASE}/writeoffs?${qs(p)}`),

  getWriteoffSummary: (p: DateRange) =>
    fetchJSON<WriteoffSummaryRow[]>(`${BASE}/writeoffs/summary?${qs(p)}`),

  getSyncStatus: () => fetchJSON<SyncStatus | null>(`${BASE}/sync/status`),

  triggerSync: () =>
    fetch(`${BASE}/sync/trigger`, { method: "POST" }).then((r) => r.json()),

  getBranches: () => fetchJSON<BranchInfo[]>(`${BASE}/branches`),
};
