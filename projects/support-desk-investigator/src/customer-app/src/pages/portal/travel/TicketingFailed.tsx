import { useState } from "react";
import { SCENARIOS } from "@/data/scenarios";
import { useScenario } from "@/hooks/useScenario";
import { LoadingStepper } from "@/components/LoadingStepper";
import { ErrorState } from "@/components/ErrorState";
import { TicketModal } from "@/components/TicketModal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { Plane } from "lucide-react";

const scenario = SCENARIOS["acme-travel-ticketing-failed"];
const steps = [
  { label: "Reserving seat" },
  { label: "Capturing payment", successOverride: true },
  { label: "Issuing ticket" },
];

export default function TicketingFailed() {
  const { state, stepStatuses, trigger, reset } = useScenario({
    steps,
    failAtStep: 2,
    delayPerStep: 1000,
    onStepComplete: (i) => {
      if (i === 1) toast.success("Payment confirmed");
    },
  });
  const [ticketOpen, setTicketOpen] = useState(false);

  return (
    <div className="container py-8 max-w-3xl">
      {state === "idle" && (
        <div className="space-y-6">
          <h1 className="text-xl font-bold">Confirm Booking</h1>

          <div className="rounded-lg border bg-card p-5">
            <div className="flex items-center gap-4">
              <div className="rounded-lg bg-brand-travel-light p-3">
                <Plane className="h-6 w-6 text-brand-travel" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-3">
                  <span className="font-bold text-lg">SFO</span>
                  <span className="text-muted-foreground">→</span>
                  <span className="font-bold text-lg">JFK</span>
                </div>
                <p className="text-sm text-muted-foreground">Economy • Feb 28, 2026</p>
              </div>
              <Badge variant="outline">$860.00</Badge>
            </div>
          </div>

          <div className="rounded-lg border bg-card p-5 space-y-3">
            <h2 className="font-semibold">Passenger Details</h2>
            <div className="grid grid-cols-2 gap-3">
              <div><Label className="text-xs">Name</Label><Input defaultValue="John Doe" className="mt-1" /></div>
              <div><Label className="text-xs">Email</Label><Input defaultValue="john.doe@acmecorp.com" className="mt-1" /></div>
            </div>
          </div>

          <div className="rounded-lg border bg-card p-5 space-y-3">
            <h2 className="font-semibold">Payment</h2>
            <div className="px-3 py-2 rounded border bg-accent/30 text-sm">Visa •••• 4242</div>
          </div>

          <Button className="w-full" onClick={trigger}>Confirm Booking</Button>
        </div>
      )}

      {state === "loading" && (
        <div className="max-w-md mx-auto py-12">
          <h2 className="text-lg font-semibold mb-4">Processing your booking…</h2>
          <LoadingStepper steps={steps} stepStatuses={stepStatuses} />
        </div>
      )}

      {state === "error" && (
        <div className="max-w-lg mx-auto py-8">
          <div className="rounded-lg border bg-success/5 border-success/20 p-4 mb-4">
            <p className="font-semibold text-success">Booking confirmed</p>
            <div className="text-sm mt-1 space-y-0.5">
              <p><span className="text-muted-foreground">Booking Ref:</span> <code className="font-mono text-xs">ACME-BKG-12345</code></p>
              <p><span className="text-muted-foreground">PNR:</span> <code className="font-mono text-xs">ABC123</code></p>
            </div>
          </div>
          <ErrorState
            scenario={scenario}
            title="Ticketing delayed"
            message="Your booking is confirmed, but we're having trouble issuing your ticket. Our team is working on it."
            onReportIssue={() => setTicketOpen(true)}
            variant="warning"
          />
        </div>
      )}

      <TicketModal open={ticketOpen} onClose={() => setTicketOpen(false)} scenario={scenario} />
    </div>
  );
}
