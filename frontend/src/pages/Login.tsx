import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { Lock, LogIn, User } from "lucide-react";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { z } from "zod";

import { api } from "../api/axios";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { useAuth } from "../context/AuthContext";

const schema = z.object({
  username: z.string().min(1, "Username is required").transform((val) => val.trim()),
  password: z.string().min(1, "Password is required"),
});

type LoginForm = z.infer<typeof schema>;

export const Login = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  const form = useForm<LoginForm>({
    resolver: zodResolver(schema),
    defaultValues: {
      username: "",
      password: "",
    },
  });

  const mutation = useMutation({
    mutationFn: async (payload: LoginForm) => {
      // Trim username before sending
      const trimmedPayload = {
        username: payload.username.trim(),
        password: payload.password,
      };
      const params = new URLSearchParams(trimmedPayload);
      return api.login(params);
    },
    onSuccess: (response) => {
      login(response.access_token, response.user);
      navigate("/dashboard");
    },
    onError: (error: any) => {
      const errorMessage = error?.response?.data?.detail || "Invalid username or password";
      form.setError("root", { message: errorMessage });
    },
  });

  const onSubmit = (values: LoginForm) => {
    // Clear any previous errors
    form.clearErrors("root");
    mutation.mutate(values);
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-4">
      <div className="w-full max-w-md">
        {/* Logo/Brand Section */}
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-600 shadow-lg">
            <LogIn className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-slate-900">MoveInSync</h1>
          <p className="mt-2 text-sm text-slate-600">Billing & Reporting Platform</p>
        </div>

        {/* Login Card */}
        <Card className="border-0 shadow-xl shadow-slate-200/50">
          <CardHeader className="space-y-1 pb-6">
            <CardTitle className="text-2xl font-semibold text-slate-900">Welcome Back</CardTitle>
            <p className="text-sm text-slate-600">Sign in to your account to continue</p>
          </CardHeader>
          <CardContent>
            <form className="space-y-5" onSubmit={form.handleSubmit(onSubmit)}>
              {/* Username Field */}
              <div className="space-y-2">
                <Label htmlFor="username" className="text-sm font-medium text-slate-700">
                  Username
                </Label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                  <Input
                    id="username"
                    autoComplete="username"
                    className="pl-10 focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter your username"
                    {...form.register("username", {
                      onChange: (e) => {
                        // Trim on blur to show user the trimmed value
                        const trimmed = e.target.value.trim();
                        if (e.target.value !== trimmed) {
                          form.setValue("username", trimmed, { shouldValidate: true });
                        }
                      },
                    })}
                    disabled={mutation.isPending}
                  />
                </div>
                {form.formState.errors.username && (
                  <p className="text-sm text-red-600 flex items-center gap-1">
                    <span className="text-red-500">•</span>
                    {form.formState.errors.username.message}
                  </p>
                )}
              </div>

              {/* Password Field */}
              <div className="space-y-2">
                <Label htmlFor="password" className="text-sm font-medium text-slate-700">
                  Password
                </Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                  <Input
                    id="password"
                    type="password"
                    autoComplete="current-password"
                    className="pl-10 focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter your password"
                    {...form.register("password")}
                    disabled={mutation.isPending}
                  />
                </div>
                {form.formState.errors.password && (
                  <p className="text-sm text-red-600 flex items-center gap-1">
                    <span className="text-red-500">•</span>
                    {form.formState.errors.password.message}
                  </p>
                )}
              </div>

              {/* Error Message */}
              {form.formState.errors.root && (
                <div className="rounded-lg border border-red-200 bg-red-50 p-3">
                  <p className="text-sm font-medium text-red-800 flex items-center gap-2">
                    <svg
                      className="h-4 w-4 shrink-0"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    {form.formState.errors.root.message}
                  </p>
                </div>
              )}

              {/* Submit Button */}
              <Button
                className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md hover:from-blue-700 hover:to-indigo-700 hover:shadow-lg transition-all duration-200"
                type="submit"
                disabled={mutation.isPending}
              >
                {mutation.isPending ? (
                  <span className="flex items-center gap-2">
                    <svg
                      className="h-4 w-4 animate-spin"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
                    Signing in...
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    <LogIn className="h-4 w-4" />
                    Sign in
                  </span>
                )}
              </Button>
            </form>

            {/* Help Text */}
            <div className="mt-6 space-y-4">
              <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                <p className="text-xs font-semibold text-slate-700 mb-3">Demo Credentials:</p>
                <div className="space-y-2 text-xs text-slate-600">
                  <div>
                    <p className="font-medium text-slate-700 mb-1">Admin:</p>
                    <p className="ml-2">admin / admin123</p>
                  </div>
                  <div>
                    <p className="font-medium text-slate-700 mb-1">Clients:</p>
                    <p className="ml-2">client1, client2, client3 / client123</p>
                  </div>
                  <div>
                    <p className="font-medium text-slate-700 mb-1">Vendors:</p>
                    <p className="ml-2">vendor1, vendor2, vendor3, vendor4 / vendor123</p>
                  </div>
                  <div>
                    <p className="font-medium text-slate-700 mb-1">Employees:</p>
                    <p className="ml-2">emp1, emp6, emp11 / emp123</p>
                  </div>
                </div>
              </div>
              
              <div className="rounded-lg border border-blue-200 bg-blue-50 p-4">
                <p className="text-xs font-semibold text-blue-900 mb-2 flex items-center gap-2">
                  <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  What you can do:
                </p>
                <ul className="space-y-1 text-xs text-blue-800 ml-6 list-disc">
                  <li>Ingest your custom trips data via CSV upload</li>
                  <li>Create and manage contracts (Admin only)</li>
                  <li>Run billing cycles and generate reports</li>
                  <li>View role-specific dashboards and analytics</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Footer */}
        <p className="mt-6 text-center text-xs text-slate-500">
          © 2025 MoveInSync. All rights reserved.
        </p>
      </div>
    </div>
  );
};
