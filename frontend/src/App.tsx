import { Navigate, Route, Routes } from "react-router-dom";

import { Navbar } from "./components/Navbar";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { useAuth } from "./context/AuthContext";
import { Contracts } from "./pages/Contracts";
import { Dashboard } from "./pages/Dashboard";
import { Login } from "./pages/Login";
import { Billing } from "./pages/Billing";
import { TripsIngest } from "./pages/TripsIngest";

function App() {
  const { token } = useAuth();

  return (
    <div className="min-h-screen bg-slate-50">
      {token && <Navbar />}
      <main className="mx-auto max-w-6xl px-4 py-8">
        <Routes>
          <Route path="/login" element={!token ? <Login /> : <Navigate to="/dashboard" replace />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/contracts"
            element={
              <ProtectedRoute>
                <Contracts />
              </ProtectedRoute>
            }
          />
          <Route
            path="/trips/ingest"
            element={
              <ProtectedRoute>
                <TripsIngest />
              </ProtectedRoute>
            }
          />
          <Route
            path="/billing"
            element={
              <ProtectedRoute>
                <Billing />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to={token ? "/dashboard" : "/login"} replace />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;