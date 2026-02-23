import { useState, useEffect } from "react";
import { SCENARIOS } from "@/data/scenarios";
import { ErrorState } from "@/components/ErrorState";
import { TicketModal } from "@/components/TicketModal";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Loader2 } from "lucide-react";

const scenario = SCENARIOS["acme-analytics-dashboard-timeout"];

export default function DashboardTimeout() {
  const [state, setState] = useState<"idle" | "loading" | "error">("idle");
  const [ticketOpen, setTicketOpen] = useState(false);

  useEffect(() => {
    if (state === "loading") {
      const t = setTimeout(() => setState("error"), 3000);
      return () => clearTimeout(t);
    }
  }, [state]);

  return (
    <div className="container py-8 max-w-5xl">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold">Revenue Overview</h1>
      </div>

      <div className="flex items-center gap-3 mb-6 flex-wrap">
        <Select defaultValue="90">
          <SelectTrigger className="w-44"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="30">Last 30 days</SelectItem>
            <SelectItem value="90">Last 90 days</SelectItem>
            <SelectItem value="365">Last 12 months</SelectItem>
          </SelectContent>
        </Select>
        <Select defaultValue="all">
          <SelectTrigger className="w-36"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Regions</SelectItem>
            <SelectItem value="us">US</SelectItem>
            <SelectItem value="eu">EU</SelectItem>
            <SelectItem value="apac">APAC</SelectItem>
          </SelectContent>
        </Select>
        <Button onClick={() => setState("loading")} disabled={state === "loading"} size="sm">
          Apply
        </Button>
      </div>

      {state === "idle" && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {["Total Revenue", "Avg. Order Value", "Conversion Rate"].map((label) => (
            <div key={label} className="rounded-lg border bg-card p-4">
              <p className="text-sm text-muted-foreground">{label}</p>
              <div className="h-24 mt-2 rounded bg-accent/50 flex items-center justify-center text-sm text-muted-foreground">
                Click Apply to load
              </div>
            </div>
          ))}
        </div>
      )}

      {state === "loading" && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="rounded-lg border bg-card p-4">
                <div className="h-4 w-24 bg-accent rounded animate-pulse-slow mb-3" />
                <div className="h-24 bg-accent rounded animate-pulse-slow" />
              </div>
            ))}
          </div>
          <div className="rounded-lg border bg-card p-4">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              Loading dashboard data…
            </div>
            <div className="mt-3 space-y-2">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="h-8 bg-accent rounded animate-pulse-slow" />
              ))}
            </div>
          </div>
        </div>
      )}

      {state === "error" && (
        <div className="max-w-lg mx-auto py-4">
          <ErrorState
            scenario={scenario}
            title="This dashboard is taking longer than expected"
            message="Try a smaller date range or refresh."
            onReportIssue={() => setTicketOpen(true)}
            onRetry={() => setState("idle")}
            retryLabel="Try last 30 days"
          />
        </div>
      )}

      {state === "idle" && (
        <div className="rounded-lg border bg-card p-4">
          <h2 className="font-semibold mb-3">Top Customers</h2>
          <div className="text-sm text-muted-foreground">Apply filters to load data</div>
        </div>
      )}

      <TicketModal open={ticketOpen} onClose={() => setTicketOpen(false)} scenario={scenario} />
    </div>
  );
}
