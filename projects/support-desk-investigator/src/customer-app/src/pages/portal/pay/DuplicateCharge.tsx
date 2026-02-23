import { useState } from "react";
import { SCENARIOS } from "@/data/scenarios";
import { useScenario } from "@/hooks/useScenario";
import { LoadingStepper } from "@/components/LoadingStepper";
import { ErrorState } from "@/components/ErrorState";
import { TicketModal } from "@/components/TicketModal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const scenario = SCENARIOS["acme-pay-duplicate-charge"];
const steps = [
  { label: "Validating payment" },
  { label: "Checking idempotency key" },
  { label: "Processing charge" },
];

export default function DuplicateCharge() {
  const { state, stepStatuses, trigger, reset } = useScenario({
    steps,
    failAtStep: 2,
    delayPerStep: 900,
  });
  const [ticketOpen, setTicketOpen] = useState(false);

  return (
    <div className="container py-8 max-w-2xl">
      {state === "idle" && (
        <div className="space-y-6">
          <h1 className="text-xl font-bold">Pay an Invoice</h1>
          <div className="rounded-lg border bg-card p-5 space-y-4">
            <div>
              <Label className="text-sm">Invoice ID</Label>
              <Input defaultValue="INV-100238" className="mt-1 font-mono" />
            </div>
            <div>
              <Label className="text-sm">Amount</Label>
              <Input defaultValue="$480.00" className="mt-1" />
            </div>
            <div>
              <Label className="text-sm">Card</Label>
              <div className="mt-1 px-3 py-2 rounded border bg-accent/30 text-sm">
                Visa •••• 4242
              </div>
            </div>
            <Button className="w-full" onClick={trigger}>Submit Payment</Button>
          </div>
        </div>
      )}

      {state === "loading" && (
        <div className="max-w-md mx-auto py-12">
          <h2 className="text-lg font-semibold mb-4">Processing payment…</h2>
          <LoadingStepper steps={steps} stepStatuses={stepStatuses} />
        </div>
      )}

      {state === "error" && (
        <div className="max-w-lg mx-auto py-8">
          <ErrorState
            scenario={scenario}
            title="Duplicate charge detected"
            message="Your original payment may still be processing."
            onReportIssue={() => setTicketOpen(true)}
            onRetry={reset}
          >
            <div className="mt-2 text-sm space-y-1">
              <p><span className="text-muted-foreground">Idempotency key:</span> <code className="font-mono text-xs">idem_pay_duplicate_demo</code></p>
              <p><span className="text-muted-foreground">Prior charge:</span> <code className="font-mono text-xs">chg_original_001</code></p>
            </div>
          </ErrorState>
        </div>
      )}

      <TicketModal open={ticketOpen} onClose={() => setTicketOpen(false)} scenario={scenario} />
    </div>
  );
}
