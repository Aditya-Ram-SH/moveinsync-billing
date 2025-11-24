import { Link, useLocation, useNavigate } from "react-router-dom";
import { Button } from "./ui/button";
import { useAuth } from "../context/AuthContext";

const getLinksForRole = (role: string | null) => {
  const allLinks = [
    { to: "/dashboard", label: "Dashboard", roles: ["ADMIN", "CLIENT", "VENDOR", "EMPLOYEE"] },
    { to: "/contracts", label: "Contracts", roles: ["ADMIN", "CLIENT", "VENDOR"] },
    { to: "/billing", label: "Billing", roles: ["ADMIN", "CLIENT", "VENDOR"] },
    { to: "/trips/ingest", label: "Trip Ingestion", roles: ["ADMIN"] },
  ];
  
  if (!role) return [];
  return allLinks.filter(link => link.roles.includes(role));
};

export const Navbar = () => {
  const { pathname } = useLocation();
  const { logout, user } = useAuth();
  const navigate = useNavigate();
  const links = getLinksForRole(user?.role || null);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const getTitle = () => {
    if (!user) return "MoveInSync";
    if (user.role === "ADMIN") return "MoveInSync Admin";
    if (user.role === "CLIENT") return "MoveInSync Client Portal";
    if (user.role === "VENDOR") return "MoveInSync Vendor Portal";
    if (user.role === "EMPLOYEE") return "MoveInSync Employee Portal";
    return "MoveInSync";
  };

  return (
    <header className="bg-white border-b border-slate-200">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
        <Link to="/dashboard" className="text-lg font-semibold text-slate-900">
          {getTitle()}
        </Link>
        <nav className="flex gap-4 text-sm font-medium text-slate-600">
          {links.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className={`rounded-md px-2 py-1 ${
                pathname.startsWith(link.to)
                  ? "bg-primary/10 text-primary"
                  : "hover:text-primary"
              }`}
            >
              {link.label}
            </Link>
          ))}
        </nav>
        <div className="flex items-center gap-4">
          {user && <span className="text-xs text-slate-500">{user.username}</span>}
          <Button variant="outline" onClick={handleLogout}>
            Logout
          </Button>
        </div>
      </div>
    </header>
  );
};

