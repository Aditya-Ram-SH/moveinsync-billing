import { useMutation, useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { api } from "../api/axios";
import { ContractDetails } from "../components/ContractDetails";
import { FormField } from "../components/FormField";
import { Select } from "../components/Select";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../components/ui/table";
import { useAuth } from "../context/AuthContext";

type ContractRow = {
  contract_id: number;
  client_id: number;
  vendor_id: number;
  client_username?: string;
  vendor_username?: string;
  model_type: string;
  version: number;
  is_active: boolean;
  config_json?: any;
  start_date?: string;
  end_date?: string;
};

const MODEL_FIELDS = {
  PACKAGE: [
    { key: "monthly_cost", label: "Monthly Cost (₹)" },
    { key: "included_km", label: "Included KM" },
    { key: "extra_km_rate", label: "Extra KM Rate (₹)" },
  ],
  TRIP: [
    { key: "base_fare", label: "Base Fare (₹)" },
    { key: "per_km_rate", label: "Per KM Rate (₹)" },
  ],
  HYBRID_A: [
    { key: "monthly_cost", label: "Monthly Minimum (₹)" },
    { key: "included_km", label: "Included KM" },
    { key: "per_trip_base", label: "Per Trip Base Fare (₹)" },
    { key: "per_km_rate", label: "Per KM Rate (₹)" },
  ],
  HYBRID_B: [
    { key: "monthly_cost", label: "Flat Trip Pay (₹)" },
    { key: "per_km_rate", label: "Extra KM Rate (₹)" },
    { key: "included_hours", label: "Included Distance (KM)" },
    { key: "extra_hour_rate", label: "Extra Distance Rate (₹)" },
  ],
} as const;

const initialConfigValues = {
  PACKAGE: { monthly_cost: "", included_km: "", extra_km_rate: "" },
  TRIP: { base_fare: "", per_km_rate: "" },
  HYBRID_A: { monthly_cost: "", included_km: "", per_trip_base: "", per_km_rate: "" },
  HYBRID_B: { monthly_cost: "", per_km_rate: "", included_hours: "", extra_hour_rate: "" },
};

export const Contracts = () => {
  const { user } = useAuth();
  const [form, setForm] = useState({
    clientId: "",
    vendorId: "",
    version: "1",
    startDate: "",
    endDate: "",
    modelType: "PACKAGE" as keyof typeof MODEL_FIELDS,
  });
  const [configValues, setConfigValues] = useState(initialConfigValues[form.modelType]);
  const [feedback, setFeedback] = useState<string>("");
  const [selectedContract, setSelectedContract] = useState<ContractRow | null>(null);
  
  const isAdmin = user?.role === "ADMIN";

  // Fetch clients and vendors for dropdowns
  const { data: clients } = useQuery({
    queryKey: ["clients"],
    queryFn: api.listClients,
    enabled: isAdmin,
  });

  const { data: vendors } = useQuery({
    queryKey: ["vendors"],
    queryFn: api.listVendors,
    enabled: isAdmin,
  });

  const { data: contracts, refetch } = useQuery({
    queryKey: ["contracts"],
    queryFn: api.listContracts,
  });

  const mutation = useMutation({
    mutationFn: (payload: any) => api.createContract(payload),
    onSuccess: () => {
      setFeedback("Contract created successfully");
      setForm((prev) => ({ ...prev, clientId: "", vendorId: "", startDate: "", endDate: "" }));
      setConfigValues(initialConfigValues[form.modelType]);
      refetch();
    },
    onError: (error: any) => {
      setFeedback(error?.response?.data?.detail ?? "Failed to create contract");
    },
  });

  const handleModelChange = (value: keyof typeof MODEL_FIELDS) => {
    setForm((prev) => ({ ...prev, modelType: value }));
    setConfigValues(initialConfigValues[value]);
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const payload = buildPayload(form, configValues);
    if (!payload) {
      setFeedback("Please fill all required fields with valid numbers.");
      return;
    }
    mutation.mutate(payload);
  };

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Contract Manager</h1>
        <p className="text-sm text-slate-500">Configure billing models for every client/vendor pair.</p>
      </div>

      <div className={`grid gap-6 ${isAdmin ? 'lg:grid-cols-3' : 'lg:grid-cols-1'}`}>
        <Card className={isAdmin ? "lg:col-span-2" : ""}>
          <CardHeader>
            <CardTitle>Contracts</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Client</TableHead>
                  <TableHead>Vendor</TableHead>
                  <TableHead>Model</TableHead>
                  <TableHead>Version</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {(contracts as ContractRow[] | undefined)?.map((contract) => (
                  <TableRow key={contract.contract_id}>
                    <TableCell>{contract.contract_id}</TableCell>
                    <TableCell>{contract.client_username || `Client #${contract.client_id}`}</TableCell>
                    <TableCell>{contract.vendor_username || `Vendor #${contract.vendor_id}`}</TableCell>
                    <TableCell>{contract.model_type}</TableCell>
                    <TableCell>{contract.version}</TableCell>
                    <TableCell>{contract.is_active ? "Active" : "Inactive"}</TableCell>
                    <TableCell>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setSelectedContract(contract)}
                      >
                        View Details
                      </Button>
                    </TableCell>
                  </TableRow>
                )) ?? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center text-sm text-slate-500">
                      No contracts available
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
            <CardTitle>Create Contract</CardTitle>
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
              <div className="grid grid-cols-2 gap-3">
                <FormField label="Version">
                  <Input
                    type="number"
                    min={1}
                    value={form.version}
                    onChange={(e) => setForm((prev) => ({ ...prev, version: e.target.value }))}
                    required
                  />
                </FormField>
                <FormField label="Model Type">
                  <Select
                    value={form.modelType}
                    onChange={(event) => handleModelChange(event.target.value as keyof typeof MODEL_FIELDS)}
                    options={[
                      { label: "Package", value: "PACKAGE" },
                      { label: "Trip", value: "TRIP" },
                      { label: "Hybrid A", value: "HYBRID_A" },
                      { label: "Hybrid B", value: "HYBRID_B" },
                    ]}
                  />
                </FormField>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <FormField label="Start Date">
                  <Input
                    type="date"
                    value={form.startDate}
                    onChange={(e) => setForm((prev) => ({ ...prev, startDate: e.target.value }))}
                    required
                  />
                </FormField>
                <FormField label="End Date">
                  <Input
                    type="date"
                    value={form.endDate}
                    onChange={(e) => setForm((prev) => ({ ...prev, endDate: e.target.value }))}
                    required
                  />
                </FormField>
              </div>

              <div className="rounded-lg border border-slate-200 p-4">
                <p className="mb-3 text-sm font-semibold text-slate-700">Configuration</p>
                <div className="grid gap-3">
                  {MODEL_FIELDS[form.modelType].map((field) => (
                    <FormField key={field.key} label={field.label}>
                      <Input
                        type="number"
                        value={configValues[field.key as keyof typeof configValues] ?? ""}
                        onChange={(e) =>
                          setConfigValues((prev) => ({
                            ...prev,
                            [field.key]: e.target.value,
                          }))
                        }
                        required
                      />
                    </FormField>
                  ))}
                </div>
              </div>

              {feedback && <p className="text-sm text-slate-600">{feedback}</p>}
              <Button type="submit" className="w-full" disabled={mutation.isPending}>
                {mutation.isPending ? "Saving..." : "Create Contract"}
              </Button>
            </form>
          </CardContent>
        </Card>
        )}
      </div>

      {/* Contract Details Modal */}
      {selectedContract && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto rounded-lg bg-white p-6 shadow-xl">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-2xl font-bold text-slate-900">Contract Details</h2>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setSelectedContract(null)}
              >
                ✕ Close
              </Button>
            </div>
            <ContractDetails contract={selectedContract as any} />
          </div>
        </div>
      )}
    </section>
  );
};

const buildPayload = (
  form: {
    clientId: string;
    vendorId: string;
    version: string;
    startDate: string;
    endDate: string;
    modelType: keyof typeof MODEL_FIELDS;
  },
  configValues: Record<string, string>,
) => {
  if (!form.clientId || !form.vendorId || !form.startDate || !form.endDate) {
    return null;
  }
  const numeric = (value: string) => Number(value || "0");

  let config: Record<string, any> = {};
  switch (form.modelType) {
    case "PACKAGE":
      config = {
        monthly_fixed_pay: numeric(configValues.monthly_cost),
        limits: { included_km: numeric(configValues.included_km) },
        vendor_payouts: { per_extra_km: numeric(configValues.extra_km_rate) },
      };
      break;
    case "TRIP":
      config = {
        rates: {
          base_fare: numeric(configValues.base_fare),
          per_km_rate: numeric(configValues.per_km_rate),
        },
      };
      break;
    case "HYBRID_A":
      config = {
        monthly_fixed_pay: numeric(configValues.monthly_cost),
        limits: { included_km: numeric(configValues.included_km) },
        rates: {
          base_fare_per_trip: numeric(configValues.per_trip_base),
          per_km_rate: numeric(configValues.per_km_rate),
        },
        guarantee: { monthly_min_payout: numeric(configValues.monthly_cost) },
      };
      break;
    case "HYBRID_B":
      config = {
        rates: {
          fixed_base_pay: numeric(configValues.monthly_cost),
          per_extra_km_rate: numeric(configValues.extra_hour_rate || configValues.per_km_rate),
        },
        thresholds: {
          included_km_per_trip: numeric(configValues.included_hours),
        },
      };
      break;
    default:
      return null;
  }

  return {
    client_username: form.clientId, // Now stores username
    vendor_username: form.vendorId, // Now stores username
    version: Number(form.version),
    start_date: form.startDate,
    end_date: form.endDate,
    model_type: form.modelType,
    config_json: config,
  };
};

