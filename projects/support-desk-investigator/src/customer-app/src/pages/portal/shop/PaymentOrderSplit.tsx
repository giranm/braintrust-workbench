import { useState } from "react";
import { SCENARIOS } from "@/data/scenarios";
import { useScenario } from "@/hooks/useScenario";
import { LoadingStepper } from "@/components/LoadingStepper";
import { ErrorState } from "@/components/ErrorState";
import { TicketModal } from "@/components/TicketModal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";

const scenario = SCENARIOS["acme-shop-payment-order-split"];
const steps = [
  { label: "Validating cart" },
  { label: "Tokenizing card" },
  { label: "Payment authorized", successOverride: true },
  { label: "Creating order" },
];

export default function PaymentOrderSplit() {
  const { state, stepStatuses, trigger, reset } = useScenario({
    steps,
    failAtStep: 3,
    delayPerStep: 900,
    onStepComplete: (i) => {
      if (i === 2) toast.success("Payment authorized");
    },
  });
  const [ticketOpen, setTicketOpen] = useState(false);

  return (
    <div className="container py-8 max-w-4xl">
      {state === "idle" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <h1 className="text-xl font-bold">Checkout</h1>
            <div className="rounded-lg border bg-card p-4">
              <h2 className="font-semibold mb-3">Cart</h2>
              <div className="flex items-center justify-between py-2 border-b">
                <div>
                  <p className="font-medium">Acme Wireless Headphones</p>
                  <p className="text-sm text-muted-foreground">Qty: 1</p>
                </div>
                <p className="font-medium">$129.00</p>
              </div>
              <div className="flex justify-between text-sm mt-2"><span className="text-muted-foreground">Shipping</span><span>$9.99</span></div>
              <div className="flex justify-between text-sm"><span className="text-muted-foreground">Tax</span><span>$11.20</span></div>
            </div>
            <div className="rounded-lg border bg-card p-4 space-y-3">
              <h2 className="font-semibold">Payment</h2>
              <div className="grid grid-cols-3 gap-3">
                <div className="col-span-3"><Label className="text-xs">Card Number</Label><Input defaultValue="4242 4242 4242 4242" className="mt-1 font-mono" /></div>
                <div><Label className="text-xs">Exp</Label><Input defaultValue="12/30" className="mt-1" /></div>
                <div><Label className="text-xs">CVC</Label><Input defaultValue="123" className="mt-1" /></div>
              </div>
            </div>
          </div>
          <div>
            <div className="rounded-lg border bg-card p-4 sticky top-20">
              <h2 className="font-semibold mb-3">Order Summary</h2>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between"><span>Subtotal</span><span>$129.00</span></div>
                <div className="flex justify-between"><span>Shipping</span><span>$9.99</span></div>
                <div className="flex justify-between"><span>Tax</span><span>$11.20</span></div>
                <div className="flex justify-between font-bold text-base border-t pt-2 mt-2"><span>Total</span><span>$150.19</span></div>
              </div>
              <Button className="w-full mt-4" onClick={trigger}>Place Order</Button>
            </div>
          </div>
        </div>
      )}

      {state === "loading" && (
        <div className="max-w-md mx-auto py-12">
          <h2 className="text-lg font-semibold mb-4">Processing your order…</h2>
          <LoadingStepper steps={steps} stepStatuses={stepStatuses} />
        </div>
      )}

      {state === "error" && (
        <div className="max-w-lg mx-auto py-8">
          <ErrorState
            scenario={scenario}
            title="Payment succeeded, but we couldn't finalize your order"
            message="Our team will investigate and contact you."
            onReportIssue={() => setTicketOpen(true)}
            variant="warning"
          >
            <div className="mt-2 text-sm space-y-1">
              <p><span className="text-muted-foreground">Payment Receipt:</span> <code className="font-mono text-xs">pay_acmeshop_split_demo</code></p>
              <p><span className="text-muted-foreground">Order confirmation:</span> <span className="text-destructive">not generated</span></p>
            </div>
          </ErrorState>
        </div>
      )}

      <TicketModal open={ticketOpen} onClose={() => setTicketOpen(false)} scenario={scenario} />
    </div>
  );
}
