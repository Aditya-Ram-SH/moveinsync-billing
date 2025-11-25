import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";

type ContractDetailsProps = {
  contract: {
    contract_id: number;
    client_id: number;
    vendor_id: number;
    client_username?: string;
    vendor_username?: string;
    model_type: string;
    config_json: any;
    version: number;
    start_date: string;
    end_date: string;
    is_active: boolean;
  };
};

export const ContractDetails = ({ contract }: ContractDetailsProps) => {
  const config = contract.config_json || {};
  const modelType = contract.model_type;
  const variant = config.variant;

  // Determine display model type
  const displayModelType = modelType === "HYBRID_A" || modelType === "HYBRID_B" ? "HYBRID" : modelType;

  return (
    <div className="space-y-6">
      {/* Contract Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">
            Contract #{contract.contract_id}
          </h2>
          <p className="text-sm text-slate-600">
            Client: {contract.client_username || `Client #${contract.client_id}`} • Vendor: {contract.vendor_username || `Vendor #${contract.vendor_id}`} • Version: {contract.version}
          </p>
        </div>
        <div className="text-right">
          <span
            className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-semibold ${
              contract.is_active
                ? "bg-green-100 text-green-700"
                : "bg-gray-100 text-gray-700"
            }`}
          >
            {contract.is_active ? "Active" : "Inactive"}
          </span>
        </div>
      </div>

      {/* Model Type Badge */}
      <div className="flex items-center gap-3">
        <span className="text-lg font-semibold text-slate-700">Model Type:</span>
        <span className="inline-flex items-center rounded-lg bg-blue-100 px-4 py-2 text-base font-bold text-blue-700">
          {displayModelType}
          {variant && (
            <span className="ml-2 text-sm font-normal">
              ({variant.replace("_", " ")})
            </span>
          )}
        </span>
      </div>

      {/* Contract Period */}
      <Card className="border-2 border-slate-200">
        <CardHeader className="bg-slate-50">
          <CardTitle className="text-lg">Contract Period</CardTitle>
        </CardHeader>
        <CardContent className="pt-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm font-semibold text-slate-600">Start Date</p>
              <p className="text-base font-semibold text-slate-900">
                {new Date(contract.start_date).toLocaleDateString("en-US", {
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                })}
              </p>
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-600">End Date</p>
              <p className="text-base font-semibold text-slate-900">
                {new Date(contract.end_date).toLocaleDateString("en-US", {
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                })}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Model-Specific Details */}
      {modelType === "PACKAGE" && (
        <div className="space-y-4">
          <Card className="border-2 border-purple-200">
            <CardHeader className="bg-purple-50">
              <CardTitle className="text-lg">💰 Monthly Fixed Payment</CardTitle>
            </CardHeader>
            <CardContent className="pt-4">
              <p className="text-3xl font-bold text-purple-700">
                ₹{config.monthly_fixed_pay?.toLocaleString("en-IN") || "0.00"}
              </p>
              <p className="text-sm text-slate-600 mt-2">
                Fixed monthly payment to vendor
              </p>
            </CardContent>
          </Card>

          <Card className="border-2 border-blue-200">
            <CardHeader className="bg-blue-50">
              <CardTitle className="text-lg">📊 Included Limits</CardTitle>
            </CardHeader>
            <CardContent className="pt-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-semibold text-slate-600">Included Kilometers</p>
                  <p className="text-2xl font-bold text-blue-700">
                    {config.limits?.included_km?.toLocaleString("en-IN") || "0"} km
                  </p>
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-600">Included Trips</p>
                  <p className="text-2xl font-bold text-blue-700">
                    {config.limits?.included_trips?.toLocaleString("en-IN") || "0"} trips
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-2 border-green-200">
            <CardHeader className="bg-green-50">
              <CardTitle className="text-lg">🚐 Vendor Performance Pay (Overage)</CardTitle>
            </CardHeader>
            <CardContent className="pt-4 space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm font-semibold text-slate-700">Per Extra KM:</span>
                <span className="text-lg font-bold text-green-700">
                  ₹{config.vendor_payouts?.per_extra_km?.toFixed(2) || "0.00"}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm font-semibold text-slate-700">Per Extra Trip:</span>
                <span className="text-lg font-bold text-green-700">
                  ₹{config.vendor_payouts?.per_extra_trip?.toFixed(2) || "0.00"}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm font-semibold text-slate-700">Night Shift Bonus:</span>
                <span className="text-lg font-bold text-green-700">
                  ₹{config.vendor_payouts?.night_shift_bonus?.toFixed(2) || "0.00"}
                </span>
              </div>
            </CardContent>
          </Card>

          <Card className="border-2 border-yellow-200">
            <CardHeader className="bg-yellow-50">
              <CardTitle className="text-lg">👤 Employee Incentives</CardTitle>
            </CardHeader>
            <CardContent className="pt-4 space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm font-semibold text-slate-700">Delay Threshold:</span>
                <span className="text-lg font-bold text-yellow-700">
                  {config.employee_incentives?.delay_threshold_min || "0"} minutes
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm font-semibold text-slate-700">Compensation Amount:</span>
                <span className="text-lg font-bold text-yellow-700">
                  ₹{config.employee_incentives?.delay_compensation_amount?.toFixed(2) || "0.00"}
                </span>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {modelType === "TRIP" && (
        <div className="space-y-4">
          <Card className="border-2 border-blue-200">
            <CardHeader className="bg-blue-50">
              <CardTitle className="text-lg">💰 Standard Rates</CardTitle>
            </CardHeader>
            <CardContent className="pt-4 space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm font-semibold text-slate-700">Base Fare:</span>
                <span className="text-lg font-bold text-blue-700">
                  ₹{config.rates?.base_fare?.toFixed(2) || "0.00"}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm font-semibold text-slate-700">Rate per KM:</span>
                <span className="text-lg font-bold text-blue-700">
                  ₹{config.rates?.per_km_rate?.toFixed(2) || "0.00"}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm font-semibold text-slate-700">Night Multiplier:</span>
                <span className="text-lg font-bold text-blue-700">
                  {config.rates?.night_multiplier || "1.0"}x
                </span>
              </div>
            </CardContent>
          </Card>

          <Card className="border-2 border-yellow-200">
            <CardHeader className="bg-yellow-50">
              <CardTitle className="text-lg">👤 Employee Incentives</CardTitle>
            </CardHeader>
            <CardContent className="pt-4 space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm font-semibold text-slate-700">Delay Threshold:</span>
                <span className="text-lg font-bold text-yellow-700">
                  {config.employee_incentives?.delay_threshold_min || "0"} minutes
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm font-semibold text-slate-700">Compensation Amount:</span>
                <span className="text-lg font-bold text-yellow-700">
                  ₹{config.employee_incentives?.delay_compensation_amount?.toFixed(2) || "0.00"}
                </span>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {modelType === "HYBRID_A" && (
        <div className="space-y-4">
          <Card className="border-2 border-blue-200">
            <CardHeader className="bg-blue-50">
              <CardTitle className="text-lg">💰 Per-Trip Rates</CardTitle>
            </CardHeader>
            <CardContent className="pt-4 space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm font-semibold text-slate-700">Base Fare per Trip:</span>
                <span className="text-lg font-bold text-blue-700">
                  ₹{config.rates?.base_fare_per_trip?.toFixed(2) || "0.00"}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm font-semibold text-slate-700">Rate per KM:</span>
                <span className="text-lg font-bold text-blue-700">
                  ₹{config.rates?.per_km_rate?.toFixed(2) || "0.00"}
                </span>
              </div>
            </CardContent>
          </Card>

          <Card className="border-2 border-green-200">
            <CardHeader className="bg-green-50">
              <CardTitle className="text-lg">🛡️ Minimum Guarantee</CardTitle>
            </CardHeader>
            <CardContent className="pt-4">
              <p className="text-3xl font-bold text-green-700">
                ₹{config.guarantee?.monthly_min_payout?.toLocaleString("en-IN") || "0.00"}
              </p>
              <p className="text-sm text-slate-600 mt-2">
                Vendor guaranteed minimum payout per month
              </p>
            </CardContent>
          </Card>

          <Card className="border-2 border-yellow-200">
            <CardHeader className="bg-yellow-50">
              <CardTitle className="text-lg">👤 Employee Incentives</CardTitle>
            </CardHeader>
            <CardContent className="pt-4 space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm font-semibold text-slate-700">Delay Threshold:</span>
                <span className="text-lg font-bold text-yellow-700">
                  {config.employee_incentives?.delay_threshold_min || "0"} minutes
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm font-semibold text-slate-700">Compensation Amount:</span>
                <span className="text-lg font-bold text-yellow-700">
                  ₹{config.employee_incentives?.delay_compensation_amount?.toFixed(2) || "0.00"}
                </span>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {modelType === "HYBRID_B" && (
        <div className="space-y-4">
          <Card className="border-2 border-blue-200">
            <CardHeader className="bg-blue-50">
              <CardTitle className="text-lg">💰 Base Tier Rates</CardTitle>
            </CardHeader>
            <CardContent className="pt-4 space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm font-semibold text-slate-700">Fixed Base Pay per Trip:</span>
                <span className="text-lg font-bold text-blue-700">
                  ₹{config.rates?.fixed_base_pay?.toFixed(2) || "0.00"}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm font-semibold text-slate-700">Rate per Extra KM:</span>
                <span className="text-lg font-bold text-blue-700">
                  ₹{config.rates?.per_extra_km_rate?.toFixed(2) || "0.00"}
                </span>
              </div>
            </CardContent>
          </Card>

          <Card className="border-2 border-purple-200">
            <CardHeader className="bg-purple-50">
              <CardTitle className="text-lg">📏 Distance Thresholds</CardTitle>
            </CardHeader>
            <CardContent className="pt-4">
              <div className="flex justify-between items-center">
                <span className="text-sm font-semibold text-slate-700">Included KM per Trip:</span>
                <span className="text-2xl font-bold text-purple-700">
                  {config.thresholds?.included_km_per_trip || "0"} km
                </span>
              </div>
              <p className="text-sm text-slate-600 mt-2">
                Distance included in fixed base pay
              </p>
            </CardContent>
          </Card>

          <Card className="border-2 border-yellow-200">
            <CardHeader className="bg-yellow-50">
              <CardTitle className="text-lg">👤 Employee Incentives</CardTitle>
            </CardHeader>
            <CardContent className="pt-4 space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm font-semibold text-slate-700">Delay Threshold:</span>
                <span className="text-lg font-bold text-yellow-700">
                  {config.employee_incentives?.delay_threshold_min || "0"} minutes
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm font-semibold text-slate-700">Compensation Amount:</span>
                <span className="text-lg font-bold text-yellow-700">
                  ₹{config.employee_incentives?.delay_compensation_amount?.toFixed(2) || "0.00"}
                </span>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

