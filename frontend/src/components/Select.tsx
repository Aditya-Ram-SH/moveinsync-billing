import { SelectHTMLAttributes } from "react";
import { cn } from "../lib/utils";

type Option = { label: string; value: string | number };

type Props = SelectHTMLAttributes<HTMLSelectElement> & {
  options: Option[];
};

export const Select = ({ options, className, ...props }: Props) => (
  <select
    className={cn(
      "w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40",
      className,
    )}
    {...props}
  >
    {options.map((option) => (
      <option key={option.value} value={option.value}>
        {option.label}
      </option>
    ))}
  </select>
);

