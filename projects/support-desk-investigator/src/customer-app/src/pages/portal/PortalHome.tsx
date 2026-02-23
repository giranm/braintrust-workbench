import { Link, useLocation } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import { PORTALS, SCENARIOS, type PortalId } from "@/data/scenarios";
import { cn } from "@/lib/utils";

const brandTextStyles: Record<string, string> = {
  shop: "text-brand-shop",
  analytics: "text-brand-analytics",
  pay: "text-brand-pay",
  travel: "text-brand-travel",
};

const brandBgStyles: Record<string, string> = {
  shop: "bg-brand-shop-light",
  analytics: "bg-brand-analytics-light",
  pay: "bg-brand-pay-light",
  travel: "bg-brand-travel-light",
};

export default function PortalHome() {
  const location = useLocation();
  const portalId = location.pathname.split("/")[2] as PortalId;
  const portal = PORTALS[portalId];
  if (!portal) return <div className="container py-12">Portal not found</div>;

  const scenarios = portal.scenarios.map((id) => SCENARIOS[id]);

  return (
    <div className="container py-8 max-w-5xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Welcome back, John</h1>
        <p className="text-muted-foreground mt-1">{portal.name} — {portal.tagline}</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-10">
        {portal.summaryCards.map((card) => (
          <div key={card.label} className="rounded-lg border bg-card p-4">
            <p className="text-sm text-muted-foreground">{card.label}</p>
            <p className="text-2xl font-bold mt-1">{card.value}</p>
            <p className="text-xs text-muted-foreground mt-1">{card.subtext}</p>
          </div>
        ))}
      </div>

      <div>
        <h2 className="text-lg font-semibold mb-4">Guided Demos</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {scenarios.map((s) => (
            <Link
              key={s.id}
              to={s.route}
              className={cn(
                "group rounded-lg border p-5 transition-all hover:shadow-md",
                brandBgStyles[portalId as string]
              )}
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className={cn("font-semibold", brandTextStyles[portalId as string])}>
                    {s.title}
                  </h3>
                  <p className="text-sm text-muted-foreground mt-1">{s.shortDescription}</p>
                  <div className="flex items-center gap-1 mt-3 text-xs font-medium text-muted-foreground">
                    <span className="bg-card border px-2 py-0.5 rounded text-xs">
                      {s.statusCode} {s.errorCode}
                    </span>
                  </div>
                </div>
                <ArrowRight className="h-5 w-5 text-muted-foreground opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all flex-shrink-0 mt-1" />
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
