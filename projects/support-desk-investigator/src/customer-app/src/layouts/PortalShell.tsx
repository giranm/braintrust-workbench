import { Link, Outlet, useLocation } from "react-router-dom";
import { ShoppingCart, BarChart3, CreditCard, Plane, ChevronDown, ArrowLeft, User } from "lucide-react";
import { ThemeToggle } from "@/components/ThemeToggle";
import { PORTALS, type PortalId } from "@/data/scenarios";
import { cn } from "@/lib/utils";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const portalIcons: Record<PortalId, React.ReactNode> = {
  shop: <ShoppingCart className="h-5 w-5" />,
  analytics: <BarChart3 className="h-5 w-5" />,
  pay: <CreditCard className="h-5 w-5" />,
  travel: <Plane className="h-5 w-5" />,
};

const brandHeaderStyles: Record<PortalId, string> = {
  shop: "bg-brand-shop",
  analytics: "bg-brand-analytics",
  pay: "bg-brand-pay",
  travel: "bg-brand-travel",
};

export function PortalShell({ portalId }: { portalId: PortalId }) {
  const portal = PORTALS[portalId];
  const location = useLocation();
  const basePath = `/portal/${portalId}`;

  return (
    <div className="min-h-screen flex flex-col">
      <header className={cn("text-primary-foreground", brandHeaderStyles[portalId])}>
        <div className="container flex h-14 items-center justify-between">
          <div className="flex items-center gap-6">
            <Link to={basePath} className="flex items-center gap-2 font-semibold">
              {portalIcons[portalId]}
              <span>{portal.name}</span>
            </Link>
            <nav className="hidden md:flex items-center gap-1">
              {portal.nav.map((item) => (
                <span
                  key={item}
                  className="px-3 py-1.5 rounded-md text-sm font-medium opacity-80 hover:opacity-100 cursor-default"
                >
                  {item}
                </span>
              ))}
            </nav>
          </div>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <DropdownMenu>
              <DropdownMenuTrigger className="flex items-center gap-2 px-2 py-1 rounded-md hover:bg-primary-foreground/10 transition-colors">
                <div className="h-7 w-7 rounded-full bg-primary-foreground/20 flex items-center justify-center">
                  <User className="h-4 w-4" />
                </div>
                <span className="text-sm font-medium hidden sm:inline">John Doe</span>
                <ChevronDown className="h-3 w-3 opacity-70" />
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <div className="px-2 py-2">
                  <p className="text-sm font-medium">John Doe</p>
                  <p className="text-xs text-muted-foreground">john.doe@acmecorp.com</p>
                </div>
                <DropdownMenuSeparator />
                <DropdownMenuItem disabled>
                  <span className="text-xs text-muted-foreground">Environment: Production</span>
                </DropdownMenuItem>
                <DropdownMenuItem disabled>
                  <span className="text-xs text-muted-foreground">Region: us-east-1</span>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild>
                  <Link to="/" className="flex items-center gap-2">
                    <ArrowLeft className="h-3 w-3" /> Exit Demo
                  </Link>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>
      <main className="flex-1 bg-background">
        <Outlet />
      </main>
      <footer className="border-t py-3">
        <div className="container flex items-center justify-between text-xs text-muted-foreground">
          <Link to="/" className="flex items-center gap-1 hover:text-foreground transition-colors">
            <ArrowLeft className="h-3 w-3" /> Exit Demo
          </Link>
          <span>Demo Environment • {portal.name}</span>
        </div>
      </footer>
    </div>
  );
}
