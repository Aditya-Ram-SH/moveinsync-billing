import { ReactNode } from "react";
import { cn } from "../lib/utils";

type Props = {
  label: string;
  htmlFor?: string;
  description?: string;
  error?: string;
  children: ReactNode;
  className?: string;
};

export const FormField = ({ label, htmlFor, description, error, children, className }: Props) => (
  <div className={cn("flex flex-col gap-1", className)}>
    <label htmlFor={htmlFor} className="text-sm font-medium text-slate-700">
      {label}
    </label>
    {children}
    {description && <p className="text-xs text-slate-500">{description}</p>}
    {error && <p className="text-xs text-red-600">{error}</p>}
  </div>
);

