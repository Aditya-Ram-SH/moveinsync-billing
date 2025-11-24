import {
  ReactNode,
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";

type UserInfo = {
  user_id: number;
  username: string;
  role: string;
  client_id: number | null;
  vendor_id: number | null;
  employee_id: number | null;
};

type AuthContextType = {
  token: string | null;
  user: UserInfo | null;
  login: (token: string, user: UserInfo) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [token, setToken] = useState<string | null>(() =>
    typeof window !== "undefined" ? localStorage.getItem("access_token") : null,
  );
  const [user, setUser] = useState<UserInfo | null>(() => {
    if (typeof window === "undefined") return null;
    const userStr = localStorage.getItem("user_info");
    return userStr ? JSON.parse(userStr) : null;
  });

  useEffect(() => {
    if (typeof window === "undefined") return;
    if (token) {
      localStorage.setItem("access_token", token);
    } else {
      localStorage.removeItem("access_token");
      localStorage.removeItem("user_info");
    }
  }, [token]);
  
  // Sync user to localStorage when it changes
  useEffect(() => {
    if (typeof window === "undefined") return;
    if (user) {
      localStorage.setItem("user_info", JSON.stringify(user));
    }
  }, [user]);

  const login = useCallback((tokenValue: string, userInfo: UserInfo) => {
    setToken(tokenValue);
    setUser(userInfo);
    if (typeof window !== "undefined") {
      localStorage.setItem("user_info", JSON.stringify(userInfo));
    }
  }, []);

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ token, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

