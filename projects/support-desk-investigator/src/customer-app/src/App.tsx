import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { SimulatorShell } from "@/layouts/SimulatorShell";
import { PortalShell } from "@/layouts/PortalShell";
import Home from "@/pages/Home";
import Settings from "@/pages/Settings";
import PortalHome from "@/pages/portal/PortalHome";
import CheckoutTimeout from "@/pages/portal/shop/CheckoutTimeout";
import PaymentOrderSplit from "@/pages/portal/shop/PaymentOrderSplit";
import DashboardTimeout from "@/pages/portal/analytics/DashboardTimeout";
import ExportFailed from "@/pages/portal/analytics/ExportFailed";
import TransferPending from "@/pages/portal/pay/TransferPending";
import DuplicateCharge from "@/pages/portal/pay/DuplicateCharge";
import TicketingFailed from "@/pages/portal/travel/TicketingFailed";
import PriceChanged from "@/pages/portal/travel/PriceChanged";
import NotFound from "@/pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route element={<SimulatorShell />}>
            <Route path="/" element={<Home />} />
            <Route path="/settings" element={<Settings />} />
          </Route>
          <Route path="/portal/shop" element={<PortalShell portalId="shop" />}>
            <Route index element={<PortalHome />} />
            <Route path="checkout-timeout" element={<CheckoutTimeout />} />
            <Route path="payment-order-split" element={<PaymentOrderSplit />} />
          </Route>
          <Route path="/portal/analytics" element={<PortalShell portalId="analytics" />}>
            <Route index element={<PortalHome />} />
            <Route path="dashboard-timeout" element={<DashboardTimeout />} />
            <Route path="export-failed" element={<ExportFailed />} />
          </Route>
          <Route path="/portal/pay" element={<PortalShell portalId="pay" />}>
            <Route index element={<PortalHome />} />
            <Route path="transfer-pending" element={<TransferPending />} />
            <Route path="duplicate-charge" element={<DuplicateCharge />} />
          </Route>
          <Route path="/portal/travel" element={<PortalShell portalId="travel" />}>
            <Route index element={<PortalHome />} />
            <Route path="ticketing-failed" element={<TicketingFailed />} />
            <Route path="price-changed" element={<PriceChanged />} />
          </Route>
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
