import { useMutation, useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { api, get, post } from "../api/axios";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { FormField } from "../components/FormField";
import { Select } from "../components/Select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../components/ui/table";
import { useAuth } from "../context/AuthContext";

type BillingRun = {
  billing_run_id: number;
  client_id: number;
  vendor_id: number;
  billing_start: string;
  billing_end: string;
  status: string;
  started_at: string;
  completed_at: string | null;
  notes: string | null;
};

type BillingRunPayload = {
  client_id: number;
  vendor_id: number;
  year: number;
  month: number;
};

export const Billing = () => {
  const { user } = useAuth();
  const [form, setForm] = useState({
    clientId: "",
    vendorId: "",
    billingYear: new Date().getFullYear().toString(),
    billingMonth: (new Date().getMonth() + 1).toString(),
  });
  const [feedback, setFeedback] = useState<string>("");
  const [lastRunId, setLastRunId] = useState<number | null>(null);
  const [selectedRunId, setSelectedRunId] = useState<number | null>(null);
  const [showAudit, setShowAudit] = useState(false);
  
  const isAdmin = user?.role === "ADMIN";

  // Fetch clients and vendors for dropdowns and name display
  const { data: clients } = useQuery({
    queryKey: ["clients"],
    queryFn: api.listClients,
  });

  const { data: vendors } = useQuery({
    queryKey: ["vendors"],
    queryFn: api.listVendors,
  });

  const { data: billingRuns, refetch, isLoading, error } = useQuery<BillingRun[]>({
    queryKey: ["billing-runs"],
    queryFn: async () => {
      const result = await get<BillingRun[]>("/billing/");
      console.log("Billing runs response:", result);
      console.log("Billing runs count:", result?.length ?? 0);
      return result;
    },
  });

  // Create lookup maps for client/vendor names
  const clientMap = new Map(clients?.map(c => [c.client_id, c.name]) || []);
  const vendorMap = new Map(vendors?.map(v => [v.vendor_id, v.name]) || []);

  const runBillingMutation = useMutation({
    mutationFn: (payload: BillingRunPayload) => post<BillingRun>("/billing/run", payload),
    onSuccess: (data) => {
      setFeedback(`Billing run #${data.billing_run_id} completed successfully!`);
      setLastRunId(data.billing_run_id);
      setForm({ 
        clientId: "", 
        vendorId: "", 
        billingYear: new Date().getFullYear().toString(),
        billingMonth: (new Date().getMonth() + 1).toString(),
      });
      refetch();
    },
    onError: (error: any) => {
      setFeedback(error?.response?.data?.detail ?? "Failed to run billing");
    },
  });

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    
    if (!form.clientId || !form.vendorId || !form.billingYear || !form.billingMonth) {
      setFeedback("Please fill all required fields.");
      return;
    }

    // Convert usernames to IDs
    const selectedClient = clients?.find(c => c.name === form.clientId);
    const selectedVendor = vendors?.find(v => v.name === form.vendorId);
    
    if (!selectedClient || !selectedVendor) {
      setFeedback("Invalid client or vendor selection.");
      return;
    }

    const payload: BillingRunPayload = {
      client_id: selectedClient.client_id,
      vendor_id: selectedVendor.vendor_id,
      year: parseInt(form.billingYear, 10),
      month: parseInt(form.billingMonth, 10),
    };

    runBillingMutation.mutate(payload);
  };

  const { data: report } = useQuery({
    queryKey: ["billing-report", selectedRunId],
    queryFn: () => api.getBillingReport(selectedRunId!),
    enabled: selectedRunId !== null,
  });

  const { data: auditLogs } = useQuery({
    queryKey: ["billing-audit", selectedRunId],
    queryFn: () => get<any[]>(`/billing/${selectedRunId}/audit`),
    enabled: selectedRunId !== null && showAudit,
  });

  const handleExport = async (runId: number) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL ?? "http://localhost:8000"}/billing/${runId}/export`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });
      
      if (!response.ok) {
        throw new Error("Export failed");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `billing_run_${runId}_report.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      setFeedback(`Exported billing run #${runId} successfully!`);
    } catch (error) {
      setFeedback("Failed to export billing run");
    }
  };

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Billing Manager</h1>
        <p className="text-sm text-slate-500">
          Run billing cycles and generate reports for clients and vendors.
        </p>
      </div>

      <div className={`grid gap-6 ${isAdmin ? 'lg:grid-cols-3' : 'lg:grid-cols-1'}`}>
        <Card className={isAdmin ? "lg:col-span-2" : ""}>
          <CardHeader>
            <CardTitle>Billing Runs History</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Run ID</TableHead>
                  <TableHead>Client</TableHead>
                  <TableHead>Vendor</TableHead>
                  <TableHead>Month</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-sm text-slate-500">
                      Loading billing runs...
                    </TableCell>
                  </TableRow>
                ) : error ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-sm text-red-500">
                      Error loading billing runs: {String(error)}
                    </TableCell>
                  </TableRow>
                ) : billingRuns && billingRuns.length > 0 ? (
                  billingRuns.map((run) => (
                    <TableRow key={run.billing_run_id}>
                      <TableCell>#{run.billing_run_id}</TableCell>
                      <TableCell>
                        {clientMap.get(run.client_id) || `Client #${run.client_id}`}
                      </TableCell>
                      <TableCell>
                        {vendorMap.get(run.vendor_id) || `Vendor #${run.vendor_id}`}
                      </TableCell>
                      <TableCell>
                        {new Date(run.billing_start).toLocaleDateString("en-US", {
                          year: "numeric",
                          month: "long",
                        })}
                      </TableCell>
                      <TableCell>
                        <span
                          className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${
                            run.status === "SUCCESS"
                              ? "bg-green-100 text-green-700"
                              : run.status === "FAILED"
                              ? "bg-red-100 text-red-700"
                              : "bg-yellow-100 text-yellow-700"
                          }`}
                        >
                          {run.status}
                        </span>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          {run.status === "SUCCESS" && (
                            <>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setSelectedRunId(run.billing_run_id)}
                              >
                                View Report
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleExport(run.billing_run_id)}
                              >
                                Download CSV
                              </Button>
                            </>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-sm text-slate-500">
                      No billing runs available
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {isAdmin && (
        <Card>
          <CardHeader>
            <CardTitle>Run Billing</CardTitle>
          </CardHeader>
          <CardContent>
            <form className="space-y-4" onSubmit={handleSubmit}>
              <FormField label="Client">
                {clients && clients.length > 0 ? (
                  <Select
                    value={form.clientId}
                    onChange={(e) => setForm((prev) => ({ ...prev, clientId: e.target.value }))}
                    required
                    options={[
                      { label: "Select a client...", value: "" },
                      ...clients.map((client) => ({
                        label: client.name,
                        value: client.name, // Store username, not ID
                      })),
                    ]}
                  />
                ) : (
                  <Input
                    type="text"
                    value="Loading clients..."
                    disabled
                  />
                )}
              </FormField>

              <FormField label="Vendor">
                {vendors && vendors.length > 0 ? (
                  <Select
                    value={form.vendorId}
                    onChange={(e) => setForm((prev) => ({ ...prev, vendorId: e.target.value }))}
                    required
                    options={[
                      { label: "Select a vendor...", value: "" },
                      ...vendors.map((vendor) => ({
                        label: vendor.name,
                        value: vendor.name, // Store username, not ID
                      })),
                    ]}
                  />
                ) : (
                  <Input
                    type="text"
                    value="Loading vendors..."
                    disabled
                  />
                )}
              </FormField>

              <FormField label="Billing Year">
                <Select
                  value={form.billingYear}
                  onChange={(e) => setForm((prev) => ({ ...prev, billingYear: e.target.value }))}
                  required
                  options={[
                    { label: "Select year...", value: "" },
                    ...Array.from({ length: 10 }, (_, i) => {
                      const year = new Date().getFullYear() - 2 + i;
                      return { label: year.toString(), value: year.toString() };
                    }),
                  ]}
                />
              </FormField>

              <FormField label="Billing Month">
                <Select
                  value={form.billingMonth}
                  onChange={(e) => setForm((prev) => ({ ...prev, billingMonth: e.target.value }))}
                  required
                  options={[
                    { label: "Select month...", value: "" },
                    { label: "January", value: "1" },
                    { label: "February", value: "2" },
                    { label: "March", value: "3" },
                    { label: "April", value: "4" },
                    { label: "May", value: "5" },
                    { label: "June", value: "6" },
                    { label: "July", value: "7" },
                    { label: "August", value: "8" },
                    { label: "September", value: "9" },
                    { label: "October", value: "10" },
                    { label: "November", value: "11" },
                    { label: "December", value: "12" },
                  ]}
                />
              </FormField>

              <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                <p className="text-xs text-slate-600">
                  <strong>Note:</strong> This will process all INGESTED trips for the selected
                  client-vendor pair in the specified month. Make sure the contract is active and
                  trips have been uploaded.
                </p>
              </div>

              {feedback && (
                <div
                  className={`rounded-lg p-3 text-sm ${
                    feedback.includes("success")
                      ? "bg-green-50 text-green-700"
                      : "bg-red-50 text-red-700"
                  }`}
                >
                  {feedback}
                </div>
              )}

              <Button
                type="submit"
                className="w-full"
                disabled={runBillingMutation.isPending}
              >
                {runBillingMutation.isPending ? "Processing..." : "Run Billing"}
              </Button>

              {lastRunId && (
                <Button
                  type="button"
                  variant="outline"
                  className="w-full"
                  onClick={() => handleExport(lastRunId)}
                >
                  Export Last Run (#{lastRunId})
                </Button>
              )}
            </form>
          </CardContent>
        </Card>
        )}
      </div>

      {/* Report View Modal */}
      {selectedRunId && report && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="relative w-full max-w-6xl max-h-[90vh] overflow-y-auto rounded-lg bg-white p-6 shadow-xl">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-2xl font-bold text-slate-900">
                Billing Report #{selectedRunId}
              </h2>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowAudit(!showAudit)}
                >
                  {showAudit ? "Hide Audit" : "Show Audit"}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setSelectedRunId(null);
                    setShowAudit(false);
                  }}
                >
                  ✕ Close
                </Button>
              </div>
            </div>

            {/* Summary */}
            <Card className="mb-4 border-2 border-blue-200">
              <CardHeader className="bg-blue-50">
                <CardTitle className="text-lg">Summary</CardTitle>
              </CardHeader>
              <CardContent className="pt-4">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <p className="text-sm font-semibold text-slate-600">Trips Processed</p>
                    <p className="text-2xl font-bold text-slate-900">{report.totals.trips_processed}</p>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-600">Vendor Payout</p>
                    <p className="text-2xl font-bold text-green-700">₹{report.totals.vendor_payout.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-600">Employee Incentives</p>
                    <p className="text-2xl font-bold text-yellow-700">₹{report.totals.employee_incentives.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-600">Final Cost</p>
                    <p className="text-2xl font-bold text-red-700">₹{report.totals.final_cost.toFixed(2)}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Charges Table */}
            <Card className="mb-4">
              <CardHeader>
                <CardTitle className="text-lg">Trip Charges</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Trip ID</TableHead>
                        <TableHead>Base Cost</TableHead>
                        <TableHead>Extra KM</TableHead>
                        <TableHead>Extra KM Cost</TableHead>
                        <TableHead>Incentive</TableHead>
                        <TableHead>Vendor Payout</TableHead>
                        <TableHead>Final Cost</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {report.charges.map((charge: any) => (
                        <TableRow key={charge.charge_id}>
                          <TableCell>{charge.trip_id}</TableCell>
                          <TableCell>₹{charge.base_cost.toFixed(2)}</TableCell>
                          <TableCell>{charge.extra_km.toFixed(2)}</TableCell>
                          <TableCell>₹{charge.extra_km_cost.toFixed(2)}</TableCell>
                          <TableCell>₹{charge.incentive_amount.toFixed(2)}</TableCell>
                          <TableCell>₹{charge.vendor_payout.toFixed(2)}</TableCell>
                          <TableCell>₹{charge.final_cost.toFixed(2)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </CardContent>
            </Card>

            {/* Audit Logs */}
            {showAudit && auditLogs && (
              <Card className="border-2 border-purple-200">
                <CardHeader className="bg-purple-50">
                  <CardTitle className="text-lg">Audit Trail</CardTitle>
                </CardHeader>
                <CardContent className="pt-4">
                  {auditLogs.length > 0 ? (
                    <div className="space-y-3">
                      {auditLogs.map((log: any) => (
                        <div
                          key={log.audit_id}
                          className="rounded-lg border border-slate-200 bg-white p-4"
                        >
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-semibold text-slate-700">
                              {log.action} - {new Date(log.timestamp).toLocaleString()}
                            </span>
                            <span className="text-xs text-slate-500">
                              Performed by User #{log.performed_by}
                            </span>
                          </div>
                          <div className="text-xs text-slate-600 bg-slate-50 p-2 rounded">
                            <pre className="whitespace-pre-wrap">
                              {JSON.stringify(log.snapshot, null, 2)}
                            </pre>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-slate-500 text-center py-4">
                      No audit logs found for this billing run.
                    </p>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      )}
    </section>
  );
};
