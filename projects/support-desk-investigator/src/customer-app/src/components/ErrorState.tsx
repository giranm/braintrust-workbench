import { useState } from "react";
import { AlertTriangle, Copy, Check, ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import type { ScenarioConfig } from "@/data/scenarios";
import { cn } from "@/lib/utils";

interface ErrorStateProps {
  scenario: ScenarioConfig;
  title: string;
  message: string;
  onReportIssue: () => void;
  onRetry?: () => void;
  retryLabel?: string;
  children?: React.ReactNode;
  variant?: "error" | "warning";
}

export function ErrorState({
  scenario,
  title,
  message,
  onReportIssue,
  onRetry,
  retryLabel = "Try again",
  children,
  variant = "error",
}: ErrorStateProps) {
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  const timestamp = new Date().toISOString();

  const diagnostics = {
    request_id: scenario.requestId,
    session_id: scenario.sessionId,
    user_id: scenario.userId,
    timestamp,
    env: "Production",
    region: "us-east-1",
    service: scenario.service,
    endpoint: scenario.endpoint,
    status_code: scenario.statusCode,
    error_code: scenario.errorCode,
    trace_id: scenario.traceId,
    span_id: scenario.spanId,
    ...scenario.extraIds,
  };

  const supportPacket = {
    ...diagnostics,
    scenario_id: scenario.id,
    company: scenario.company,
    workflow: scenario.workflow,
    evidence: scenario.evidence,
  };

  const copyDiagnostics = () => {
    navigator.clipboard.writeText(JSON.stringify(supportPacket, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-4">
      <div
        className={cn(
          "rounded-lg border p-4",
          variant === "error"
            ? "bg-destructive/5 border-destructive/20"
            : "bg-warning/5 border-warning/20"
        )}
      >
        <div className="flex items-start gap-3">
          <AlertTriangle
            className={cn(
              "h-5 w-5 mt-0.5 flex-shrink-0",
              variant === "error" ? "text-destructive" : "text-warning"
            )}
          />
          <div className="flex-1 space-y-2">
            <h3 className="font-semibold text-foreground">{title}</h3>
            <p className="text-sm text-muted-foreground">{message}</p>
            {children}
            <div className="flex items-center gap-2 pt-2">
              <Button onClick={onReportIssue} size="sm">
                Report Issue
              </Button>
              {onRetry && (
                <Button onClick={onRetry} variant="outline" size="sm">
                  {retryLabel}
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>

      <Collapsible open={detailsOpen} onOpenChange={setDetailsOpen}>
        <CollapsibleTrigger className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors">
          <ChevronDown
            className={cn("h-4 w-4 transition-transform", detailsOpen && "rotate-180")}
          />
          Error Details
        </CollapsibleTrigger>
        <CollapsibleContent className="mt-3 space-y-4">
          <div className="rounded-lg border bg-card p-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
              {Object.entries(diagnostics).map(([key, value]) => (
                <div key={key}>
                  <span className="text-muted-foreground font-mono text-xs">{key}</span>
                  <p className="font-mono text-xs mt-0.5 break-all">{String(value)}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-lg border bg-card p-4 space-y-3">
            <h4 className="text-sm font-medium">Log Excerpt</h4>
            <pre className="text-xs font-mono bg-accent/50 rounded p-3 overflow-x-auto whitespace-pre-wrap">
              {scenario.evidence.logExcerpt}
            </pre>
            <div>
              <span className="text-xs text-muted-foreground">Suggested log query:</span>
              <code className="block text-xs font-mono bg-accent/50 rounded p-2 mt-1 break-all">
                {scenario.evidence.suggestedLogQuery}
              </code>
            </div>
            <Button variant="outline" size="sm" onClick={copyDiagnostics}>
              {copied ? (
                <>
                  <Check className="h-3 w-3 mr-1" /> Copied
                </>
              ) : (
                <>
                  <Copy className="h-3 w-3 mr-1" /> Copy support packet
                </>
              )}
            </Button>
          </div>
        </CollapsibleContent>
      </Collapsible>
    </div>
  );
}
