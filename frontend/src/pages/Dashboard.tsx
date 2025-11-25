import { useQuery } from "@tanstack/react-query";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, AreaChart, Area } from "recharts";

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
    client_username?: string;
    vendor_username?: string;
    billing_start: string;
    billing_end: string;
    status: string;
    started_at: string;
    completed_at: string | null;
    notes: string | null;
  } | null;
};

type EmployeeTrip = {
  trip_id: number;
  trip_type: string;
  start_time: string;
  end_time: string;
  booking_time: string | null;
  distance_km: number;
  duration_min: number;
  status: string;
  vehicle_type: string | null;
  vehicle_number: string | null;
  incentive_amount: number;
  has_charge: boolean;
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
          System-wide overview and statistics
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

      {/* Trip Status */}
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
          title="Vendor Payout" 
          value={`₹${stats.total_vendor_payout.toFixed(2)}`} 
          color="green"
        />
        <MetricCard 
          title="Employee Incentives" 
          value={`₹${stats.total_employee_incentives.toFixed(2)}`} 
          color="yellow"
        />
      </div>

      {/* Recent Billing Run */}
      {stats.recent_billing_run && (
        <Card>
          <CardHeader>
            <CardTitle>Recent Billing Run</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <p className="text-sm text-slate-600">
                Run #{stats.recent_billing_run.billing_run_id} - {new Date(stats.recent_billing_run.billing_start).toLocaleDateString("en-US", { year: "numeric", month: "long" })}
              </p>
              <p className="text-sm text-slate-600">
                Status: <span className="font-semibold">{stats.recent_billing_run.status}</span>
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </section>
  );
};

const ClientDashboard = ({ stats, user }: { stats: DashboardStats; user: any }) => {
  const { data: analytics, isLoading: analyticsLoading } = useQuery({
    queryKey: ["client-analytics"],
    queryFn: () => api.getClientAnalytics(),
    enabled: user?.role === "CLIENT",
  });

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

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

      {/* Charts Row 1 */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Cost Trends Over Time */}
        <Card>
          <CardHeader>
            <CardTitle>Cost Trends Over Time</CardTitle>
          </CardHeader>
          <CardContent>
            {analyticsLoading ? (
              <div className="h-64 flex items-center justify-center">Loading...</div>
            ) : analytics?.cost_trends && analytics.cost_trends.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={analytics.cost_trends}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip formatter={(value: number) => `₹${value.toFixed(2)}`} />
                  <Legend />
                  <Line type="monotone" dataKey="total_cost" stroke="#FF8042" strokeWidth={2} name="Total Cost (₹)" />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-64 flex items-center justify-center text-slate-500">
                No billing data available
              </div>
            )}
          </CardContent>
        </Card>

        {/* Cost Breakdown by Vendor */}
        <Card>
          <CardHeader>
            <CardTitle>Cost Breakdown by Vendor</CardTitle>
          </CardHeader>
          <CardContent>
            {analyticsLoading ? (
              <div className="h-64 flex items-center justify-center">Loading...</div>
            ) : analytics?.cost_by_vendor && analytics.cost_by_vendor.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={analytics.cost_by_vendor}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ vendor_name, percent }) => `${vendor_name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="total_cost"
                  >
                    {analytics.cost_by_vendor.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number) => `₹${value.toFixed(2)}`} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-64 flex items-center justify-center text-slate-500">
                No vendor data available
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Charts Row 2 */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Trips Over Time */}
        <Card>
          <CardHeader>
            <CardTitle>Trips Over Time</CardTitle>
          </CardHeader>
          <CardContent>
            {analyticsLoading ? (
              <div className="h-64 flex items-center justify-center">Loading...</div>
            ) : analytics?.trips_over_time && analytics.trips_over_time.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={analytics.trips_over_time}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="trip_count" stroke="#8884d8" strokeWidth={2} name="Trips" />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-64 flex items-center justify-center text-slate-500">
                No trip data available
              </div>
            )}
          </CardContent>
        </Card>

        {/* Trip Status Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Trip Status Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            {analyticsLoading ? (
              <div className="h-64 flex items-center justify-center">Loading...</div>
            ) : analytics?.trip_status_distribution && analytics.trip_status_distribution.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={analytics.trip_status_distribution}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ status, percent }) => `${status} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="count"
                  >
                    {analytics.trip_status_distribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-64 flex items-center justify-center text-slate-500">
                No status data available
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Charts Row 3 */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Distance Over Time */}
        <Card>
          <CardHeader>
            <CardTitle>Distance Traveled Over Time</CardTitle>
          </CardHeader>
          <CardContent>
            {analyticsLoading ? (
              <div className="h-64 flex items-center justify-center">Loading...</div>
            ) : analytics?.distance_over_time && analytics.distance_over_time.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={analytics.distance_over_time}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip formatter={(value: number) => `${value.toFixed(1)} km`} />
                  <Legend />
                  <Area type="monotone" dataKey="total_distance" stroke="#00C49F" fill="#00C49F" fillOpacity={0.6} name="Distance (km)" />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-64 flex items-center justify-center text-slate-500">
                No distance data available
              </div>
            )}
          </CardContent>
        </Card>

        {/* Billing Runs Timeline */}
        <Card>
          <CardHeader>
            <CardTitle>Billing Runs Timeline</CardTitle>
          </CardHeader>
          <CardContent>
            {analyticsLoading ? (
              <div className="h-64 flex items-center justify-center">Loading...</div>
            ) : analytics?.billing_runs_timeline && analytics.billing_runs_timeline.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={analytics.billing_runs_timeline}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="billing_start" tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short' })} />
                  <YAxis />
                  <Tooltip 
                    formatter={(value: number) => `₹${value.toFixed(2)}`}
                    labelFormatter={(value) => `Month: ${new Date(value).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}`}
                  />
                  <Legend />
                  <Bar dataKey="total_cost" fill="#FF8042" name="Total Cost (₹)" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-64 flex items-center justify-center text-slate-500">
                No billing runs available
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recent Billing */}
      {stats.recent_billing_run && (
        <Card>
          <CardHeader>
            <CardTitle>Recent Billing Run</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <p className="text-sm text-slate-600">
                Run #{stats.recent_billing_run.billing_run_id} - {new Date(stats.recent_billing_run.billing_start).toLocaleDateString("en-US", { year: "numeric", month: "long" })}
              </p>
              <p className="text-sm text-slate-600">
                Status: <span className="font-semibold">{stats.recent_billing_run.status}</span>
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </section>
  );
};

const VendorDashboard = ({ stats, user }: { stats: DashboardStats; user: any }) => {
  const { data: analytics, isLoading: analyticsLoading } = useQuery({
    queryKey: ["vendor-analytics"],
    queryFn: () => api.getVendorAnalytics(),
    enabled: user?.role === "VENDOR",
  });

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

  return (
    <section className="space-y-8">
      <div className="flex flex-col gap-2">
        <h1 className="text-4xl font-bold text-slate-900">Vendor Dashboard</h1>
        <p className="text-base text-slate-600">
          Your vendor operations and earnings overview
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
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
        <MetricCard 
          title="Billing Runs" 
          value={stats.total_billing_runs} 
          icon="💰"
          color="green"
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
          title="Total Payout" 
          value={`₹${stats.total_vendor_payout.toFixed(2)}`} 
          color="green"
          large
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Payout Trends Over Time */}
        <Card>
          <CardHeader>
            <CardTitle>Payout Trends Over Time</CardTitle>
          </CardHeader>
          <CardContent>
            {analyticsLoading ? (
              <div className="h-64 flex items-center justify-center">Loading...</div>
            ) : analytics?.payout_trends && analytics.payout_trends.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={analytics.payout_trends}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip formatter={(value: number) => `₹${value.toFixed(2)}`} />
                  <Legend />
                  <Line type="monotone" dataKey="total_payout" stroke="#00C49F" strokeWidth={2} name="Total Payout (₹)" />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-64 flex items-center justify-center text-slate-500">
                No payout data available
              </div>
            )}
          </CardContent>
        </Card>

        {/* Payout Breakdown by Client */}
        <Card>
          <CardHeader>
            <CardTitle>Payout Breakdown by Client</CardTitle>
          </CardHeader>
          <CardContent>
            {analyticsLoading ? (
              <div className="h-64 flex items-center justify-center">Loading...</div>
            ) : analytics?.payout_by_client && analytics.payout_by_client.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={analytics.payout_by_client}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ client_name, percent }) => `${client_name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="total_payout"
                  >
                    {analytics.payout_by_client.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number) => `₹${value.toFixed(2)}`} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-64 flex items-center justify-center text-slate-500">
                No client data available
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Charts Row 2 */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Trips Over Time */}
        <Card>
          <CardHeader>
            <CardTitle>Trips Over Time</CardTitle>
          </CardHeader>
          <CardContent>
            {analyticsLoading ? (
              <div className="h-64 flex items-center justify-center">Loading...</div>
            ) : analytics?.trips_over_time && analytics.trips_over_time.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={analytics.trips_over_time}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="trip_count" stroke="#8884d8" strokeWidth={2} name="Trips" />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-64 flex items-center justify-center text-slate-500">
                No trip data available
              </div>
            )}
          </CardContent>
        </Card>

        {/* Trip Status Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Trip Status Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            {analyticsLoading ? (
              <div className="h-64 flex items-center justify-center">Loading...</div>
            ) : analytics?.trip_status_distribution && analytics.trip_status_distribution.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={analytics.trip_status_distribution}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ status, percent }) => `${status} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="count"
                  >
                    {analytics.trip_status_distribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-64 flex items-center justify-center text-slate-500">
                No status data available
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Charts Row 3 */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Distance Over Time */}
        <Card>
          <CardHeader>
            <CardTitle>Distance Traveled Over Time</CardTitle>
          </CardHeader>
          <CardContent>
            {analyticsLoading ? (
              <div className="h-64 flex items-center justify-center">Loading...</div>
            ) : analytics?.distance_over_time && analytics.distance_over_time.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={analytics.distance_over_time}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip formatter={(value: number) => `${value.toFixed(1)} km`} />
                  <Legend />
                  <Area type="monotone" dataKey="total_distance" stroke="#00C49F" fill="#00C49F" fillOpacity={0.6} name="Distance (km)" />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-64 flex items-center justify-center text-slate-500">
                No distance data available
              </div>
            )}
          </CardContent>
        </Card>

        {/* Billing Runs Timeline */}
        <Card>
          <CardHeader>
            <CardTitle>Billing Runs Timeline</CardTitle>
          </CardHeader>
          <CardContent>
            {analyticsLoading ? (
              <div className="h-64 flex items-center justify-center">Loading...</div>
            ) : analytics?.billing_runs_timeline && analytics.billing_runs_timeline.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={analytics.billing_runs_timeline}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="billing_start" tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short' })} />
                  <YAxis />
                  <Tooltip 
                    formatter={(value: number) => `₹${value.toFixed(2)}`}
                    labelFormatter={(value) => `Month: ${new Date(value).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}`}
                  />
                  <Legend />
                  <Bar dataKey="total_payout" fill="#00C49F" name="Total Payout (₹)" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-64 flex items-center justify-center text-slate-500">
                No billing runs available
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recent Billing */}
      {stats.recent_billing_run && (
        <Card>
          <CardHeader>
            <CardTitle>Recent Billing Run</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <p className="text-sm text-slate-600">
                Run #{stats.recent_billing_run.billing_run_id} - {new Date(stats.recent_billing_run.billing_start).toLocaleDateString("en-US", { year: "numeric", month: "long" })}
              </p>
              <p className="text-sm text-slate-600">
                Status: <span className="font-semibold">{stats.recent_billing_run.status}</span>
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </section>
  );
};

const EmployeeDashboard = ({ stats, user }: { stats: DashboardStats; user: any }) => {
  const { data: trips, isLoading: tripsLoading } = useQuery<EmployeeTrip[]>({
    queryKey: ["employee-trips", user.employee_id],
    queryFn: () => api.getEmployeeTrips(),
    enabled: user?.role === "EMPLOYEE" && !!user?.employee_id,
  });

  // Process trips for charts
  const tripsData = trips || [];
  
  // Group trips by date for line chart
  const tripsByDate = tripsData.reduce((acc, trip) => {
    if (!trip.start_time) return acc;
    const date = new Date(trip.start_time).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    if (!acc[date]) {
      acc[date] = { date, trips: 0, distance: 0, incentives: 0 };
    }
    acc[date].trips += 1;
    acc[date].distance += trip.distance_km;
    acc[date].incentives += trip.incentive_amount;
    return acc;
  }, {} as Record<string, { date: string; trips: number; distance: number; incentives: number }>);
  
  const chartData = Object.values(tripsByDate).slice(-14).sort((a, b) => 
    new Date(a.date).getTime() - new Date(b.date).getTime()
  );

  // Trip type distribution
  const tripTypeData = tripsData.reduce((acc, trip) => {
    const type = trip.trip_type || 'UNKNOWN';
    acc[type] = (acc[type] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);
  
  const pieData = Object.entries(tripTypeData).map(([name, value]) => ({ name, value }));
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

  // Status distribution
  const statusData = tripsData.reduce((acc, trip) => {
    const status = trip.status || 'UNKNOWN';
    acc[status] = (acc[status] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);
  
  const statusChartData = Object.entries(statusData).map(([name, value]) => ({ name, value }));

  // Calculate totals
  const totalIncentives = tripsData.reduce((sum, trip) => sum + trip.incentive_amount, 0);
  const totalDistance = tripsData.reduce((sum, trip) => sum + trip.distance_km, 0);
  const tripsWithIncentives = tripsData.filter(t => t.incentive_amount > 0).length;

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

      {/* Key Metrics */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
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
        />
        <MetricCard 
          title="Total Incentives" 
          value={`₹${stats.total_employee_incentives.toFixed(2)}`} 
          icon="💰"
          color="yellow"
          large
        />
        <MetricCard 
          title="Processed Trips" 
          value={stats.processed_trips} 
          subtitle={`of ${stats.total_trips} total`}
          color="green"
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Trips Over Time */}
        <Card>
          <CardHeader>
            <CardTitle>Trips Over Time</CardTitle>
          </CardHeader>
          <CardContent>
            {tripsLoading ? (
              <div className="h-64 flex items-center justify-center">Loading...</div>
            ) : chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="trips" stroke="#8884d8" strokeWidth={2} name="Trips" />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-64 flex items-center justify-center text-slate-500">
                No trip data available
              </div>
            )}
          </CardContent>
        </Card>

        {/* Trip Type Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Trip Type Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            {tripsLoading ? (
              <div className="h-64 flex items-center justify-center">Loading...</div>
            ) : pieData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-64 flex items-center justify-center text-slate-500">
                No trip data available
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Charts Row 2 */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Distance Over Time */}
        <Card>
          <CardHeader>
            <CardTitle>Distance Traveled Over Time</CardTitle>
          </CardHeader>
          <CardContent>
            {tripsLoading ? (
              <div className="h-64 flex items-center justify-center">Loading...</div>
            ) : chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="distance" fill="#00C49F" name="Distance (km)" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-64 flex items-center justify-center text-slate-500">
                No trip data available
              </div>
            )}
          </CardContent>
        </Card>

        {/* Trip Status */}
        <Card>
          <CardHeader>
            <CardTitle>Trip Status Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            {tripsLoading ? (
              <div className="h-64 flex items-center justify-center">Loading...</div>
            ) : statusChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={statusChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="value" fill="#FF8042" name="Count" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-64 flex items-center justify-center text-slate-500">
                No trip data available
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Incentives Chart */}
      {chartData.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Incentives Earned Over Time</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip formatter={(value: number) => `₹${value.toFixed(2)}`} />
                <Legend />
                <Line type="monotone" dataKey="incentives" stroke="#FFBB28" strokeWidth={2} name="Incentives (₹)" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* Recent Trips Table */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Trip History</CardTitle>
        </CardHeader>
        <CardContent>
          {tripsLoading ? (
            <div className="py-8 text-center text-slate-500">Loading trips...</div>
          ) : tripsData.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-2">Trip ID</th>
                    <th className="text-left p-2">Type</th>
                    <th className="text-left p-2">Date</th>
                    <th className="text-left p-2">Distance</th>
                    <th className="text-left p-2">Duration</th>
                    <th className="text-left p-2">Status</th>
                    <th className="text-right p-2">Incentive</th>
                  </tr>
                </thead>
                <tbody>
                  {tripsData.slice(0, 10).map((trip) => (
                    <tr key={trip.trip_id} className="border-b hover:bg-slate-50">
                      <td className="p-2 font-medium">#{trip.trip_id}</td>
                      <td className="p-2">
                        <span className="rounded-full bg-blue-100 px-2 py-1 text-xs text-blue-700">
                          {trip.trip_type || 'N/A'}
                        </span>
                      </td>
                      <td className="p-2">
                        {trip.start_time 
                          ? new Date(trip.start_time).toLocaleDateString('en-US', { 
                              month: 'short', 
                              day: 'numeric',
                              year: 'numeric'
                            })
                          : 'N/A'}
                      </td>
                      <td className="p-2">{trip.distance_km.toFixed(1)} km</td>
                      <td className="p-2">{trip.duration_min} min</td>
                      <td className="p-2">
                        <span className={`rounded-full px-2 py-1 text-xs font-semibold ${
                          trip.status === "PROCESSED"
                            ? "bg-green-100 text-green-700"
                            : trip.status === "ERROR"
                            ? "bg-red-100 text-red-700"
                            : "bg-yellow-100 text-yellow-700"
                        }`}>
                          {trip.status}
                        </span>
                      </td>
                      <td className="p-2 text-right font-semibold">
                        {trip.incentive_amount > 0 ? (
                          <span className="text-yellow-700">₹{trip.incentive_amount.toFixed(2)}</span>
                        ) : (
                          <span className="text-slate-400">₹0.00</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="py-8 text-center text-slate-500">
              No trips found. Your trips will appear here once they are recorded.
            </div>
          )}
        </CardContent>
      </Card>
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
  <div className="flex flex-col">
    <p className="text-sm text-slate-600">{label}</p>
    <p className="text-2xl font-bold text-slate-900">{value}</p>
  </div>
);
