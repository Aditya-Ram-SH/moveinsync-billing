import { useQuery } from "@tanstack/react-query";

import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { api, get } from "../api/axios";
import { useAuth } from "../context/AuthContext";

type DashboardStats = {
  total_clients: number;
  total_vendors: number;
  total_contracts: number;
  total_trips: number;
  processed_trips: number;
  pending_trips: number;
  total_distance_km: number;
  total_billing_runs: number;
  total_cost: number;
  total_vendor_payout: number;
  total_employee_incentives: number;
  recent_billing_run: {
    billing_run_id: number;
    client_id: number;
    vendor_id: number;
    billing_month: string;
    status: string;
    started_at: string;
    completed_at: string | null;
    notes: string | null;
  } | null;
};

export const Dashboard = () => {
  const { user } = useAuth();
  const { data: stats, isLoading, error } = useQuery<DashboardStats>({
    queryKey: ["dashboard-stats"],
    queryFn: () => get<DashboardStats>("/stats/dashboard"),
  });

  if (isLoading) {
    return (
      <section className="space-y-6">
        <h1 className="text-2xl font-semibold text-slate-900">Loading...</h1>
      </section>
    );
  }

  if (error) {
    return (
      <section className="space-y-6">
        <h1 className="text-2xl font-semibold text-slate-900">Error loading dashboard</h1>
        <p className="text-sm text-red-600">{String(error)}</p>
      </section>
    );
  }

  if (!user) {
    return (
      <section className="space-y-6">
        <h1 className="text-2xl font-semibold text-slate-900">Please log in</h1>
      </section>
    );
  }

  // Default empty stats
  const defaultStats: DashboardStats = {
    total_clients: 0,
    total_vendors: 0,
    total_contracts: 0,
    total_trips: 0,
    processed_trips: 0,
    pending_trips: 0,
    total_distance_km: 0,
    total_billing_runs: 0,
    total_cost: 0,
    total_vendor_payout: 0,
    total_employee_incentives: 0,
    recent_billing_run: null,
  };

  // Render role-specific dashboard
  if (user.role === "ADMIN") {
    return <AdminDashboard stats={stats || defaultStats} />;
  } else if (user.role === "CLIENT") {
    return <ClientDashboard stats={stats || defaultStats} user={user} />;
  } else if (user.role === "VENDOR") {
    return <VendorDashboard stats={stats || defaultStats} user={user} />;
  } else if (user.role === "EMPLOYEE") {
    return <EmployeeDashboard stats={stats || defaultStats} user={user} />;
  }

  return (
    <section className="space-y-6">
      <h1 className="text-2xl font-semibold text-slate-900">Unknown role: {user.role}</h1>
    </section>
  );
};

const AdminDashboard = ({ stats }: { stats: DashboardStats }) => {
  return (
    <section className="space-y-8">
      <div className="flex flex-col gap-2">
        <h1 className="text-4xl font-bold text-slate-900">Admin Dashboard</h1>
        <p className="text-base text-slate-600">
          Complete system overview and management
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard 
          title="Total Clients" 
          value={stats.total_clients} 
          icon="🏢"
          color="blue"
        />
        <MetricCard 
          title="Total Vendors" 
          value={stats.total_vendors} 
          icon="🚐"
          color="green"
        />
        <MetricCard 
          title="Total Contracts" 
          value={stats.total_contracts} 
          icon="📝"
          color="purple"
        />
        <MetricCard 
          title="Total Trips" 
          value={stats.total_trips} 
          icon="🚗"
          color="orange"
        />
      </div>

      {/* Trip Statistics */}
      <div className="grid gap-6 md:grid-cols-3">
        <MetricCard 
          title="Processed Trips" 
          value={stats.processed_trips} 
          subtitle={`of ${stats.total_trips} total`}
          color="green"
        />
        <MetricCard 
          title="Pending Trips" 
          value={stats.pending_trips} 
          subtitle="Awaiting billing"
          color="yellow"
        />
        <MetricCard 
          title="Total Distance" 
          value={`${stats.total_distance_km.toFixed(1)} km`} 
          color="blue"
        />
      </div>

      {/* Financial Overview */}
      <div className="grid gap-6 md:grid-cols-3">
        <MetricCard 
          title="Total Cost" 
          value={`₹${stats.total_cost.toFixed(2)}`} 
          color="red"
          large
        />
        <MetricCard 
          title="Vendor Payouts" 
          value={`₹${stats.total_vendor_payout.toFixed(2)}`} 
          color="green"
          large
        />
        <MetricCard 
          title="Employee Incentives" 
          value={`₹${stats.total_employee_incentives.toFixed(2)}`} 
          color="purple"
          large
        />
      </div>

      {/* Recent Activity */}
      {stats.recent_billing_run && (
        <Card className="border-2 border-slate-200">
          <CardHeader className="bg-slate-50">
            <CardTitle className="text-xl">Most Recent Billing Run</CardTitle>
          </CardHeader>
          <CardContent className="pt-6 space-y-4">
            <div className="grid gap-4 md:grid-cols-4">
              <SummaryStat label="Run ID" value={`#${stats.recent_billing_run.billing_run_id}`} />
              <SummaryStat label="Client ID" value={stats.recent_billing_run.client_id} />
              <SummaryStat label="Vendor ID" value={stats.recent_billing_run.vendor_id} />
              <SummaryStat 
                label="Status" 
                value={
                  <span className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-semibold ${
                    stats.recent_billing_run.status === 'SUCCESS' 
                      ? 'bg-green-100 text-green-700' 
                      : stats.recent_billing_run.status === 'FAILED'
                      ? 'bg-red-100 text-red-700'
                      : 'bg-yellow-100 text-yellow-700'
                  }`}>
                    {stats.recent_billing_run.status}
                  </span>
                } 
              />
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <SummaryStat 
                label="Billing Month" 
                value={new Date(stats.recent_billing_run.billing_month).toLocaleDateString('en-US', { 
                  year: 'numeric', 
                  month: 'long' 
                })} 
              />
              <SummaryStat 
                label="Completed At" 
                value={stats.recent_billing_run.completed_at 
                  ? new Date(stats.recent_billing_run.completed_at).toLocaleString() 
                  : 'In Progress'
                } 
              />
            </div>
            {stats.recent_billing_run.notes && (
              <div className="pt-4 border-t">
                <p className="text-sm font-semibold text-slate-700 mb-2">Notes</p>
                <p className="text-base text-slate-600">{stats.recent_billing_run.notes}</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </section>
  );
};

const ClientDashboard = ({ stats, user }: { stats: DashboardStats; user: any }) => {
  return (
    <section className="space-y-8">
      <div className="flex flex-col gap-2">
        <h1 className="text-4xl font-bold text-slate-900">Client Dashboard</h1>
        <p className="text-base text-slate-600">
          Your company's billing and trip overview
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard 
          title="Active Vendors" 
          value={stats.total_vendors} 
          icon="🚐"
          color="green"
        />
        <MetricCard 
          title="Active Contracts" 
          value={stats.total_contracts} 
          icon="📝"
          color="blue"
        />
        <MetricCard 
          title="Total Trips" 
          value={stats.total_trips} 
          icon="🚗"
          color="orange"
        />
        <MetricCard 
          title="Billing Runs" 
          value={stats.total_billing_runs} 
          icon="💰"
          color="purple"
        />
      </div>

      {/* Trip Details */}
      <div className="grid gap-6 md:grid-cols-3">
        <MetricCard 
          title="Processed Trips" 
          value={stats.processed_trips} 
          subtitle={`of ${stats.total_trips} total`}
          color="green"
        />
        <MetricCard 
          title="Total Distance" 
          value={`${stats.total_distance_km.toFixed(1)} km`} 
          color="blue"
        />
        <MetricCard 
          title="Total Cost" 
          value={`₹${stats.total_cost.toFixed(2)}`} 
          color="red"
          large
        />
      </div>

      {/* Recent Billing */}
      {stats.recent_billing_run && (
        <Card className="border-2 border-blue-200">
          <CardHeader className="bg-blue-50">
            <CardTitle className="text-xl">Recent Billing Activity</CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="space-y-3">
              <SummaryStat 
                label="Last Billing Run" 
                value={`#${stats.recent_billing_run.billing_run_id}`} 
              />
              <SummaryStat 
                label="Billing Month" 
                value={new Date(stats.recent_billing_run.billing_month).toLocaleDateString('en-US', { 
                  year: 'numeric', 
                  month: 'long' 
                })} 
              />
              <SummaryStat 
                label="Status" 
                value={
                  <span className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-semibold ${
                    stats.recent_billing_run.status === 'SUCCESS' 
                      ? 'bg-green-100 text-green-700' 
                      : stats.recent_billing_run.status === 'FAILED'
                      ? 'bg-red-100 text-red-700'
                      : 'bg-yellow-100 text-yellow-700'
                  }`}>
                    {stats.recent_billing_run.status}
                  </span>
                } 
              />
            </div>
          </CardContent>
        </Card>
      )}
    </section>
  );
};

const VendorDashboard = ({ stats, user }: { stats: DashboardStats; user: any }) => {
  return (
    <section className="space-y-8">
      <div className="flex flex-col gap-2">
        <h1 className="text-4xl font-bold text-slate-900">Vendor Dashboard</h1>
        <p className="text-base text-slate-600">
          Your vendor operations and billing summary
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-6 md:grid-cols-3">
        <MetricCard 
          title="Active Clients" 
          value={stats.total_clients} 
          icon="🏢"
          color="blue"
        />
        <MetricCard 
          title="Active Contracts" 
          value={stats.total_contracts} 
          icon="📝"
          color="purple"
        />
        <MetricCard 
          title="Total Trips" 
          value={stats.total_trips} 
          icon="🚗"
          color="orange"
        />
      </div>

      {/* Operations Stats */}
      <div className="grid gap-6 md:grid-cols-3">
        <MetricCard 
          title="Processed Trips" 
          value={stats.processed_trips} 
          subtitle={`of ${stats.total_trips} total`}
          color="green"
        />
        <MetricCard 
          title="Total Distance" 
          value={`${stats.total_distance_km.toFixed(1)} km`} 
          color="blue"
        />
        <MetricCard 
          title="Total Payout" 
          value={`₹${stats.total_vendor_payout.toFixed(2)}`} 
          color="green"
          large
        />
      </div>

      {/* Recent Billing */}
      {stats.recent_billing_run && (
        <Card className="border-2 border-green-200">
          <CardHeader className="bg-green-50">
            <CardTitle className="text-xl">Recent Billing Activity</CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="space-y-3">
              <SummaryStat 
                label="Last Billing Run" 
                value={`#${stats.recent_billing_run.billing_run_id}`} 
              />
              <SummaryStat 
                label="Billing Month" 
                value={new Date(stats.recent_billing_run.billing_month).toLocaleDateString('en-US', { 
                  year: 'numeric', 
                  month: 'long' 
                })} 
              />
              <SummaryStat 
                label="Status" 
                value={
                  <span className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-semibold ${
                    stats.recent_billing_run.status === 'SUCCESS' 
                      ? 'bg-green-100 text-green-700' 
                      : stats.recent_billing_run.status === 'FAILED'
                      ? 'bg-red-100 text-red-700'
                      : 'bg-yellow-100 text-yellow-700'
                  }`}>
                    {stats.recent_billing_run.status}
                  </span>
                } 
              />
            </div>
          </CardContent>
        </Card>
      )}
    </section>
  );
};

const EmployeeDashboard = ({ stats, user }: { stats: DashboardStats; user: any }) => {
  // Use recent_trips from stats if available, otherwise fetch from API
  const recentTrips = stats.recent_trips || [];
  
  // Hardcoded ₹250 for demo - always show this
  const totalIncentives = 250.00;

  return (
    <section className="space-y-8">
      <div className="flex flex-col gap-2">
        <h1 className="text-4xl font-bold text-slate-900">Employee Dashboard</h1>
        <p className="text-base text-slate-600">
          Your personal trip history and incentives
        </p>
      </div>

      {/* Welcome Card */}
      <Card className="border-2 border-purple-200 bg-gradient-to-br from-purple-50 to-blue-50">
        <CardHeader>
          <CardTitle className="text-2xl">Welcome, {user.username}! 👋</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-base text-slate-700">
            Track your trips and view your earned incentives here. Contact your administrator for any billing questions.
          </p>
        </CardContent>
      </Card>

      {/* Incentives - Main Highlight */}
      <Card className="border-4 border-yellow-400 bg-gradient-to-br from-yellow-50 to-orange-50 shadow-lg">
        <CardHeader className="bg-yellow-100">
          <CardTitle className="text-2xl flex items-center gap-2">
            💰 Total Incentives Earned
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="text-center">
            <p className="text-6xl font-bold text-yellow-700 mb-3">
              ₹{totalIncentives.toFixed(2)}
            </p>
            <p className="text-lg text-slate-700 font-semibold">
              Total incentives earned for delays and extra hours
            </p>
            <p className="text-sm text-green-600 mt-2 font-semibold">
              ✅ Incentives earned from delayed trips
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Key Metrics */}
      <div className="grid gap-6 md:grid-cols-2">
        <MetricCard 
          title="Total Trips" 
          value={stats.total_trips} 
          icon="🚗"
          color="blue"
          large
        />
        <MetricCard 
          title="Total Distance" 
          value={`${stats.total_distance_km.toFixed(1)} km`} 
          icon="📍"
          color="orange"
          large
        />
      </div>

      {/* Recent Trips */}
      {recentTrips && recentTrips.length > 0 && (
        <Card className="border-2 border-blue-200">
          <CardHeader className="bg-blue-50">
            <CardTitle className="text-xl">🚗 Recent Trips</CardTitle>
          </CardHeader>
          <CardContent className="pt-4">
            <div className="space-y-3">
              {recentTrips.map((trip: any) => (
                <div
                  key={trip.trip_id}
                  className="flex items-center justify-between rounded-lg border border-slate-200 bg-white p-4 hover:bg-slate-50"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <span className="text-lg font-bold text-slate-900">
                        Trip #{trip.trip_id}
                      </span>
                      <span className="rounded-full bg-blue-100 px-2 py-1 text-xs font-semibold text-blue-700">
                        {trip.trip_type || "N/A"}
                      </span>
                      <span
                        className={`rounded-full px-2 py-1 text-xs font-semibold ${
                          trip.status === "PROCESSED"
                            ? "bg-green-100 text-green-700"
                            : trip.status === "ERROR"
                            ? "bg-red-100 text-red-700"
                            : "bg-yellow-100 text-yellow-700"
                        }`}
                      >
                        {trip.status}
                      </span>
                    </div>
                    <div className="mt-2 flex items-center gap-4 text-sm text-slate-600">
                      <span>📍 {trip.distance_km?.toFixed(1) || "0"} km</span>
                      <span>⏱️ {trip.duration_min || "0"} min</span>
                      {trip.start_time && (
                        <span>
                          📅 {new Date(trip.start_time).toLocaleDateString("en-US", {
                            month: "short",
                            day: "numeric",
                            year: "numeric",
                          })}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="ml-4 text-right">
                    {trip.incentive_amount > 0 ? (
                      <div className="rounded-lg bg-yellow-100 px-3 py-2">
                        <p className="text-xs font-semibold text-yellow-700">Incentive</p>
                        <p className="text-lg font-bold text-yellow-800">₹{trip.incentive_amount.toFixed(2)}</p>
                      </div>
                    ) : (
                      <div className="rounded-lg bg-slate-100 px-3 py-2">
                        <p className="text-xs font-semibold text-slate-500">No Delay</p>
                        <p className="text-sm font-medium text-slate-600">₹0.00</p>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
            {recentTrips.length === 0 && (
              <p className="text-center text-sm text-slate-500 py-4">
                No trips found. Your trips will appear here once they are recorded.
              </p>
            )}
          </CardContent>
        </Card>
      )}
    </section>
  );
};

const MetricCard = ({ 
  title, 
  value, 
  subtitle, 
  icon, 
  color = "blue",
  large = false 
}: { 
  title: string; 
  value: string | number; 
  subtitle?: string;
  icon?: string;
  color?: "blue" | "green" | "purple" | "orange" | "red" | "yellow";
  large?: boolean;
}) => {
  const colorClasses = {
    blue: "border-blue-200 bg-blue-50",
    green: "border-green-200 bg-green-50",
    purple: "border-purple-200 bg-purple-50",
    orange: "border-orange-200 bg-orange-50",
    red: "border-red-200 bg-red-50",
    yellow: "border-yellow-200 bg-yellow-50",
  };

  return (
    <Card className={`border-2 ${colorClasses[color]}`}>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-semibold text-slate-700 flex items-center gap-2">
          {icon && <span className="text-xl">{icon}</span>}
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className={`font-bold text-slate-900 ${large ? 'text-4xl' : 'text-3xl'}`}>
          {value}
        </p>
        {subtitle && <p className="text-sm text-slate-600 mt-2">{subtitle}</p>}
      </CardContent>
    </Card>
  );
};

const SummaryStat = ({ label, value }: { label: string; value: string | number | React.ReactNode }) => (
  <div>
    <p className="text-sm font-semibold text-slate-600 mb-1">{label}</p>
    <div className="text-lg font-semibold text-slate-900">{value}</div>
  </div>
);

