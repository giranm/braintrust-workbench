import { useState, useEffect } from "react";
import { SCENARIOS } from "@/data/scenarios";
import { ErrorState } from "@/components/ErrorState";
import { TicketModal } from "@/components/TicketModal";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { Download, Loader2 } from "lucide-react";

const scenario = SCENARIOS["acme-analytics-export-failed"];

const fakeData = [
  { id: "C-001", name: "Acme Corp", lastActivity: "2026-02-18", spend: "$12,450" },
  { id: "C-002", name: "Globex Inc", lastActivity: "2026-02-19", spend: "$8,200" },
  { id: "C-003", name: "Initech LLC", lastActivity: "2026-02-17", spend: "$5,780" },
  { id: "C-004", name: "Umbrella Co", lastActivity: "2026-02-20", spend: "$15,320" },
  { id: "C-005", name: "Stark Industries", lastActivity: "2026-02-15", spend: "$22,100" },
];

export default function ExportFailed() {
  const [state, setState] = useState<"idle" | "exporting" | "error">("idle");
  const [progress, setProgress] = useState(0);
  const [ticketOpen, setTicketOpen] = useState(false);

  useEffect(() => {
    if (state === "exporting") {
      const interval = setInterval(() => {
        setProgress((p) => {
          if (p >= 45) {
            clearInterval(interval);
            setTimeout(() => {
              setState("error");
              toast.error("Export failed");
            }, 500);
            return 45;
          }
          return p + 5;
        });
      }, 200);
      return () => clearInterval(interval);
    }
  }, [state]);

  const startExport = () => {
    setProgress(0);
    setState("exporting");
    toast.info("Export job started — job_analytics_export_demo");
  };

  return (
    <div className="container py-8 max-w-5xl">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold">Customer Activity Report</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="rounded-lg border bg-card overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-accent/30">
                  <th className="text-left p-3 font-medium">Customer ID</th>
                  <th className="text-left p-3 font-medium">Name</th>
                  <th className="text-left p-3 font-medium">Last Activity</th>
                  <th className="text-right p-3 font-medium">Total Spend</th>
                </tr>
              </thead>
              <tbody>
                {fakeData.map((row) => (
                  <tr key={row.id} className="border-b last:border-0">
                    <td className="p-3 font-mono text-xs">{row.id}</td>
                    <td className="p-3">{row.name}</td>
                    <td className="p-3 text-muted-foreground">{row.lastActivity}</td>
                    <td className="p-3 text-right">{row.spend}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="p-3 text-xs text-muted-foreground border-t">
              Showing 5 of 15,420 rows
            </div>
          </div>
        </div>

        <div>
          <div className="rounded-lg border bg-card p-4 sticky top-20 space-y-4">
            <h2 className="font-semibold">Export Options</h2>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Format</p>
              <div className="px-3 py-2 rounded border bg-accent/30 text-sm">CSV</div>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Columns</p>
              <div className="text-xs text-muted-foreground">customer_id, name, last_activity, total_spend</div>
            </div>

            {state === "exporting" && (
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Generating file ({progress}%)
                </div>
                <div className="h-2 bg-accent rounded-full overflow-hidden">
                  <div className="h-full bg-primary transition-all" style={{ width: `${progress}%` }} />
                </div>
              </div>
            )}

            <Button
              className="w-full gap-2"
              onClick={startExport}
              disabled={state === "exporting"}
            >
              <Download className="h-4 w-4" />
              Export CSV
            </Button>
          </div>
        </div>
      </div>

      {state === "error" && (
        <div className="max-w-lg mx-auto py-6">
          <ErrorState
            scenario={scenario}
            title="We couldn't generate your export"
            message="Please try again."
            onReportIssue={() => setTicketOpen(true)}
            onRetry={() => setState("idle")}
          />
        </div>
      )}

      <TicketModal open={ticketOpen} onClose={() => setTicketOpen(false)} scenario={scenario} />
    </div>
  );
}
