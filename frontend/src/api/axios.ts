import axios from "axios";
import type { AxiosRequestConfig } from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers = {
      ...config.headers,
      Authorization: `Bearer ${token}`,
    };
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
    }
    return Promise.reject(error);
  },
);

export const get = <T = unknown>(url: string, config?: AxiosRequestConfig) =>
  apiClient.get<T>(url, config).then((res) => res.data);

export const post = <T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig) =>
  apiClient.post<T>(url, data, config).then((res) => res.data);

export const put = <T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig) =>
  apiClient.put<T>(url, data, config).then((res) => res.data);

export const del = <T = unknown>(url: string, config?: AxiosRequestConfig) =>
  apiClient.delete<T>(url, config).then((res) => res.data);

export const api = {
  login: (form: URLSearchParams) => post<{ 
    access_token: string; 
    token_type: string;
    user: {
      user_id: number;
      username: string;
      role: string;
      client_id: number | null;
      vendor_id: number | null;
      employee_id: number | null;
    };
  }>("/auth/token", form),
  listContracts: () => get<any[]>("/contracts"),
  createContract: (payload: any) => post("/contracts", payload),
  ingestTrips: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return post<{ rows_ingested: number }>("/trips/ingest-csv", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  runBilling: (payload: { client_id: number; vendor_id: number; year: number; month: number }) =>
    post<{ billing_run_id: number; status: string; notes?: string }>("/billing/run", payload),
  listBillingRuns: () => get<any[]>("/billing/"),
  getBillingReport: (id: number) => get<{
    billing_run: any;
    totals: { trips_processed: number; vendor_payout: number; employee_incentives: number; final_cost: number };
    charges: any[];
  }>(`/billing/${id}/report`),
  getDashboardStats: () => get<any>("/stats/dashboard"),
  getClientAnalytics: () => get<{
    cost_trends: Array<{ month: string; total_cost: number; trip_count: number }>;
    cost_by_vendor: Array<{ vendor_id: number; vendor_name: string; total_cost: number; trip_count: number }>;
    trips_over_time: Array<{ month: string; trip_count: number }>;
    trip_status_distribution: Array<{ status: string; count: number }>;
    distance_over_time: Array<{ month: string; total_distance: number }>;
    billing_runs_timeline: Array<{
      billing_run_id: number;
      billing_start: string;
      billing_end: string;
      status: string;
      total_cost: number;
      started_at: string;
    }>;
  }>("/stats/client-analytics"),
  getVendorAnalytics: () => get<{
    payout_trends: Array<{ month: string; total_payout: number; trip_count: number }>;
    payout_by_client: Array<{ client_id: number; client_name: string; total_payout: number; trip_count: number }>;
    trips_over_time: Array<{ month: string; trip_count: number }>;
    trip_status_distribution: Array<{ status: string; count: number }>;
    distance_over_time: Array<{ month: string; total_distance: number }>;
    billing_runs_timeline: Array<{
      billing_run_id: number;
      billing_start: string;
      billing_end: string;
      status: string;
      total_payout: number;
      started_at: string;
    }>;
  }>("/stats/vendor-analytics"),
  listTrips: () => get<any[]>("/trips/"),
  getEmployeeTrips: () => get<any[]>("/trips/employee/my-trips"),
  listClients: () => get<{ client_id: number; name: string }[]>("/clients"),
  listVendors: () => get<{ vendor_id: number; name: string }[]>("/vendors"),
};

export { apiClient };
