import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Loader2, CheckCircle2, ExternalLink } from "lucide-react";
import type { ScenarioConfig } from "@/data/scenarios";

interface TicketModalProps {
  open: boolean;
  onClose: () => void;
  scenario: ScenarioConfig;
}

type SubmitState = "idle" | "submitting" | "success" | "error";

export function TicketModal({ open, onClose, scenario }: TicketModalProps) {
  const [subject, setSubject] = useState(scenario.subject);
  const [description, setDescription] = useState(scenario.ticketDescription);
  const [steps, setSteps] = useState(scenario.stepsToReproduce);
  const [impact, setImpact] = useState(scenario.impact);
  const [name, setName] = useState("John Doe");
  const [email, setEmail] = useState("john.doe@acmecorp.com");
  const [attachDiag, setAttachDiag] = useState(true);
  const [submitState, setSubmitState] = useState<SubmitState>("idle");
  const [ticketId, setTicketId] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  const handleSubmit = async () => {
    const frappeEndpoint = localStorage.getItem("frappe-endpoint") || "";
    if (!frappeEndpoint) {
      setErrorMsg("No Frappe API endpoint configured. Go to Settings to set it up.");
      setSubmitState("error");
      return;
    }

    setSubmitState("submitting");
    const timestamp = new Date().toISOString();

    const payload = {
      subject,
      description,
      steps_to_reproduce: steps,
      impact,
      reporter_name: name,
      reporter_email: email,
      company: scenario.company,
      scenario_id: scenario.id,
      workflow: scenario.workflow,
      context: {
        timestamp,
        env: "prod",
        region: "us-east-1",
        service: scenario.service,
        endpoint: scenario.endpoint,
        status_code: scenario.statusCode,
        error_code: scenario.errorCode,
        request_id: scenario.requestId,
        session_id: scenario.sessionId,
        user_id: scenario.userId,
        trace_id: scenario.traceId,
        span_id: scenario.spanId,
        ...scenario.extraIds,
      },
      ...(attachDiag ? { evidence: scenario.evidence } : {}),
    };

    try {
      const res = await fetch(frappeEndpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setTicketId(data?.name || data?.ticket_id || "Submitted");
      setSubmitState("success");
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to submit ticket");
      setSubmitState("error");
    }
  };

  const handleClose = () => {
    setSubmitState("idle");
    setErrorMsg("");
    setTicketId("");
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Submit Support Ticket</DialogTitle>
        </DialogHeader>

        {submitState === "success" ? (
          <div className="text-center py-6 space-y-4">
            <CheckCircle2 className="h-12 w-12 text-success mx-auto" />
            <div>
              <p className="font-semibold text-lg">Ticket submitted</p>
              {ticketId && (
                <p className="text-sm text-muted-foreground mt-1">ID: {ticketId}</p>
              )}
            </div>
            <div className="flex flex-col gap-2">
              <Button variant="outline" className="gap-2">
                <ExternalLink className="h-4 w-4" />
                Continue to Braintrust demo
              </Button>
              <Button variant="ghost" onClick={handleClose}>
                Close
              </Button>
            </div>
          </div>
        ) : (
          <>
            <div className="space-y-4">
              <div>
                <Label htmlFor="subject">Subject</Label>
                <Input id="subject" value={subject} onChange={(e) => setSubject(e.target.value)} />
              </div>
              <div>
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={3}
                />
              </div>
              <div>
                <Label htmlFor="steps">Steps to Reproduce</Label>
                <Textarea
                  id="steps"
                  value={steps}
                  onChange={(e) => setSteps(e.target.value)}
                  rows={2}
                />
              </div>
              <div>
                <Label>Impact</Label>
                <Select value={impact} onValueChange={(v: any) => setImpact(v)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <Label htmlFor="name">Reporter Name</Label>
                  <Input id="name" value={name} onChange={(e) => setName(e.target.value)} />
                </div>
                <div>
                  <Label htmlFor="email">Reporter Email</Label>
                  <Input id="email" value={email} onChange={(e) => setEmail(e.target.value)} />
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Checkbox
                  id="diag"
                  checked={attachDiag}
                  onCheckedChange={(v) => setAttachDiag(!!v)}
                />
                <Label htmlFor="diag" className="text-sm font-normal cursor-pointer">
                  Attach diagnostics
                </Label>
              </div>
              {submitState === "error" && (
                <p className="text-sm text-destructive">{errorMsg}</p>
              )}
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={handleClose}>
                Cancel
              </Button>
              <Button onClick={handleSubmit} disabled={submitState === "submitting"}>
                {submitState === "submitting" && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                Submit Ticket
              </Button>
            </DialogFooter>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
