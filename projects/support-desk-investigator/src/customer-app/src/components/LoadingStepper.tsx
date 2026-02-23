import { CheckCircle2, XCircle, Loader2 } from "lucide-react";
import type { StepStatus, StepConfig } from "@/hooks/useScenario";
import { cn } from "@/lib/utils";

interface LoadingStepperProps {
  steps: StepConfig[];
  stepStatuses: StepStatus[];
}

export function LoadingStepper({ steps, stepStatuses }: LoadingStepperProps) {
  return (
    <div className="space-y-3 py-4">
      {steps.map((step, i) => {
        const status = stepStatuses[i];
        return (
          <div key={i} className="flex items-center gap-3">
            <div className="flex-shrink-0">
              {status === "done" && <CheckCircle2 className="h-5 w-5 text-success" />}
              {status === "error" && <XCircle className="h-5 w-5 text-destructive" />}
              {status === "loading" && <Loader2 className="h-5 w-5 text-primary animate-spin" />}
              {status === "pending" && (
                <div className="h-5 w-5 rounded-full border-2 border-muted" />
              )}
            </div>
            <span
              className={cn(
                "text-sm",
                status === "done" && "text-success",
                status === "error" && "text-destructive font-medium",
                status === "loading" && "text-foreground font-medium",
                status === "pending" && "text-muted-foreground"
              )}
            >
              {step.label}
            </span>
          </div>
        );
      })}
    </div>
  );
}
