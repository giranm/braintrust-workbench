import { useState, useCallback, useRef } from "react";

export type StepStatus = "pending" | "loading" | "done" | "error";
export type ScenarioState = "idle" | "loading" | "error";

export interface StepConfig {
  label: string;
  successOverride?: boolean; // true = show green check even on fail scenario (like payment captured)
}

interface UseScenarioOptions {
  steps: StepConfig[];
  failAtStep: number; // 0-indexed step that fails
  delayPerStep?: number; // ms per step
  onStepComplete?: (stepIndex: number) => void;
}

export function useScenario(options: UseScenarioOptions) {
  const { steps, failAtStep, delayPerStep = 800, onStepComplete } = options;
  const [state, setState] = useState<ScenarioState>("idle");
  const [currentStep, setCurrentStep] = useState(-1);
  const [stepStatuses, setStepStatuses] = useState<StepStatus[]>(steps.map(() => "pending"));
  const timeoutRef = useRef<number[]>([]);

  const clearTimeouts = () => {
    timeoutRef.current.forEach(clearTimeout);
    timeoutRef.current = [];
  };

  const trigger = useCallback(() => {
    clearTimeouts();
    setState("loading");
    setCurrentStep(0);
    setStepStatuses(steps.map(() => "pending"));

    steps.forEach((step, i) => {
      // Start loading this step
      const loadTimeout = window.setTimeout(() => {
        setCurrentStep(i);
        setStepStatuses((prev) => {
          const next = [...prev];
          next[i] = "loading";
          return next;
        });
      }, i * delayPerStep);
      timeoutRef.current.push(loadTimeout);

      // Complete or fail this step
      const completeTimeout = window.setTimeout(() => {
        if (i < failAtStep || step.successOverride) {
          setStepStatuses((prev) => {
            const next = [...prev];
            next[i] = "done";
            return next;
          });
          onStepComplete?.(i);
        } else if (i === failAtStep) {
          setStepStatuses((prev) => {
            const next = [...prev];
            next[i] = "error";
            return next;
          });
          setState("error");
        }
      }, (i + 1) * delayPerStep);
      timeoutRef.current.push(completeTimeout);
    });
  }, [steps, failAtStep, delayPerStep, onStepComplete]);

  const reset = useCallback(() => {
    clearTimeouts();
    setState("idle");
    setCurrentStep(-1);
    setStepStatuses(steps.map(() => "pending"));
  }, [steps]);

  return { state, currentStep, stepStatuses, steps, trigger, reset };
}
