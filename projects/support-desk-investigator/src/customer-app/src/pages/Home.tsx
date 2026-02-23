import { Link } from "react-router-dom";
import { ShoppingCart, BarChart3, CreditCard, Plane, ArrowRight } from "lucide-react";
import type { PortalId } from "@/data/scenarios";
import { PORTALS } from "@/data/scenarios";
import { cn } from "@/lib/utils";

const portalIcons: Record<PortalId, React.ReactNode> = {
  shop: <ShoppingCart className="h-8 w-8" />,
  analytics: <BarChart3 className="h-8 w-8" />,
  pay: <CreditCard className="h-8 w-8" />,
  travel: <Plane className="h-8 w-8" />,
};

const brandGradients: Record<PortalId, string> = {
  shop: "brand-gradient-shop",
  analytics: "brand-gradient-analytics",
  pay: "brand-gradient-pay",
  travel: "brand-gradient-travel",
};

const scenarioCounts: Record<PortalId, number> = {
  shop: 2,
  analytics: 2,
  pay: 2,
  travel: 2,
};

export default function Home() {
  const portals = Object.entries(PORTALS) as [PortalId, (typeof PORTALS)[PortalId]][];

  return (
    <div className="container py-12 max-w-4xl">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold tracking-tight mb-2">Support Desk Failure Simulator</h1>
        <p className="text-muted-foreground max-w-lg mx-auto">
          Choose an industry portal to explore realistic failure scenarios. Each generates a support
          ticket for the Braintrust demo.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {portals.map(([id, portal]) => (
          <Link
            key={id}
            to={`/portal/${id}`}
            className="group rounded-xl border bg-card hover:shadow-lg transition-all duration-200 overflow-hidden"
          >
            <div
              className={cn(
                "h-2",
                brandGradients[id]
              )}
            />
            <div className="p-6">
              <div className="flex items-start justify-between">
                <div
                  className={cn(
                    "rounded-lg p-3 text-primary-foreground",
                    brandGradients[id]
                  )}
                >
                  {portalIcons[id]}
                </div>
                <ArrowRight className="h-5 w-5 text-muted-foreground opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all" />
              </div>
              <h2 className="text-xl font-semibold mt-4">{portal.name}</h2>
              <p className="text-sm text-muted-foreground mt-1">{portal.tagline}</p>
              <p className="text-xs text-muted-foreground mt-3">
                {scenarioCounts[id]} failure scenarios
              </p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
