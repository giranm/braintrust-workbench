import { useState } from "react";
import { SCENARIOS } from "@/data/scenarios";
import { ErrorState } from "@/components/ErrorState";
import { TicketModal } from "@/components/TicketModal";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Plane } from "lucide-react";

const scenario = SCENARIOS["acme-travel-price-changed"];

export default function PriceChanged() {
  const [state, setState] = useState<"idle" | "priceAlert" | "error">("idle");
  const [ticketOpen, setTicketOpen] = useState(false);

  return (
    <div className="container py-8 max-w-3xl">
      <div className="space-y-6">
        <h1 className="text-xl font-bold">Flight Checkout</h1>

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
            <div className="text-right">
              {(state === "priceAlert" || state === "error") ? (
                <div>
                  <span className="line-through text-muted-foreground text-sm">$860.00</span>
                  <p className="font-bold text-lg text-destructive">$1,060.00</p>
                </div>
              ) : (
                <Badge variant="outline" className="text-base">$860.00</Badge>
              )}
            </div>
          </div>
        </div>

        <div className="rounded-lg border bg-card p-5 space-y-2">
          <p className="text-sm"><span className="text-muted-foreground">Passenger:</span> John Doe</p>
          <p className="text-sm"><span className="text-muted-foreground">Card:</span> Visa •••• 4242</p>
        </div>

        {state === "idle" && (
          <Button className="w-full" onClick={() => setState("priceAlert")}>
            Continue
          </Button>
        )}

        {state === "priceAlert" && (
          <div className="rounded-lg border border-warning/30 bg-warning/5 p-4 space-y-3">
            <h3 className="font-semibold">The price changed while you were checking out</h3>
            <p className="text-sm text-muted-foreground">
              The fare increased from $860.00 to $1,060.00 (+$200.00).
            </p>
            <div className="flex gap-2">
              <Button onClick={() => setState("error")} size="sm">Accept new price</Button>
              <Button variant="outline" size="sm" onClick={() => setState("idle")}>Cancel</Button>
            </div>
          </div>
        )}

        {state === "error" && (
          <ErrorState
            scenario={scenario}
            title="We couldn't lock the price"
            message="Please try again."
            onReportIssue={() => setTicketOpen(true)}
            onRetry={() => setState("idle")}
          >
            <div className="mt-2 text-sm space-y-1">
              <p><span className="text-muted-foreground">Old price:</span> $860.00</p>
              <p><span className="text-muted-foreground">New price:</span> $1,060.00</p>
            </div>
          </ErrorState>
        )}
      </div>

      <TicketModal open={ticketOpen} onClose={() => setTicketOpen(false)} scenario={scenario} />
    </div>
  );
}
