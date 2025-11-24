import { cn } from "../../lib/utils";

type BadgeProps = React.HTMLAttributes<HTMLSpanElement> & {
  variant?: "default" | "success" | "warning";
};

export const Badge = ({ className, variant = "default", ...props }: BadgeProps) => {
  const variantClass =
    variant === "success"
      ? "bg-green-100 text-green-700"
      : variant === "warning"
        ? "bg-yellow-100 text-yellow-700"
        : "bg-primary/10 text-primary";

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        variantClass,
        className,
      )}
      {...props}
    />
  );
};

