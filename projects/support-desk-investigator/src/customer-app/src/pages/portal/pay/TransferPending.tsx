import { useState, useEffect } from "react";
import { SCENARIOS } from "@/data/scenarios";
import { ErrorState } from "@/components/ErrorState";
import { TicketModal } from "@/components/TicketModal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Loader2 } from "lucide-react";

const scenario = SCENARIOS["acme-pay-transfer-pending"];

export default function TransferPending() {
  const [state, setState] = useState<"idle" | "sent" | "warning">("idle");
  const [ticketOpen, setTicketOpen] = useState(false);

  useEffect(() => {
    if (state === "sent") {
      const t = setTimeout(() => setState("warning"), 3000);
      return () => clearTimeout(t);
    }
  }, [state]);

  return (
    <div className="container py-8 max-w-2xl">
      {state === "idle" && (
        <div className="space-y-6">
          <h1 className="text-xl font-bold">New Transfer</h1>
          <div className="rounded-lg border bg-card p-5 space-y-4">
            <div>
              <Label className="text-sm">From</Label>
              <div className="mt-1 px-3 py-2 rounded border bg-accent/30 text-sm">
                Acme Pay Balance (…1234)
              </div>
            </div>
            <div>
              <Label className="text-sm">To</Label>
              <div className="mt-1 px-3 py-2 rounded border bg-accent/30 text-sm">
                Demo Bank •••• 6789
              </div>
            </div>
            <div>
              <Label htmlFor="amount" className="text-sm">Amount</Label>
              <Input id="amount" defaultValue="$2,500.00" className="mt-1" />
            </div>
            <div>
              <Label htmlFor="memo" className="text-sm">Memo</Label>
              <Input id="memo" defaultValue="Vendor payout" className="mt-1" />
            </div>
            <Button className="w-full" onClick={() => setState("sent")}>
              Send Transfer
            </Button>
          </div>
        </div>
      )}

      {(state === "sent" || state === "warning") && (
        <div className="space-y-6">
          <h1 className="text-xl font-bold">Transfer Details</h1>
          <div className="rounded-lg border bg-card p-5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Transfer ID</span>
              <code className="font-mono text-xs">txf_pay_pending_demo</code>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Amount</span>
              <span className="font-medium">$2,500.00</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Status</span>
              <Badge variant="outline" className="bg-warning/10 text-warning border-warning/30">
                {state === "sent" && <Loader2 className="h-3 w-3 mr-1 animate-spin" />}
                Pending
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Created</span>
              <span className="text-sm">{new Date().toLocaleString()}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">ETA</span>
              <span className="text-sm">Usually &lt; 10 minutes</span>
            </div>
          </div>

          {state === "warning" && (
            <ErrorState
              scenario={scenario}
              title="This transfer is taking longer than expected"
              message="If it remains pending, contact support."
              onReportIssue={() => setTicketOpen(true)}
              variant="warning"
            />
          )}
        </div>
      )}

      <TicketModal open={ticketOpen} onClose={() => setTicketOpen(false)} scenario={scenario} />
    </div>
  );
}
