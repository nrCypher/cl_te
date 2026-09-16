"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { StepIndicator } from "@/components/step-indicator";
import { useProposal } from "@/hooks/use-proposal";
import { ProjectInfo } from "@/components/steps/project-info";
import { ScopeDefinition } from "@/components/steps/scope-definition";
import { Stakeholders } from "@/components/steps/stakeholders";
import { BusinessProcess } from "@/components/steps/business-process";
import { FunctionalRequirements } from "@/components/steps/functional-requirements";
import { NonFunctionalRequirements } from "@/components/steps/non-functional-requirements";
import { AIRecommendations } from "@/components/steps/ai-recommendations";
import { ReviewExport } from "@/components/steps/review-export";

const TOTAL_STEPS = 8;

const STEP_COMPONENTS = [ProjectInfo, ScopeDefinition, Stakeholders, BusinessProcess, FunctionalRequirements, NonFunctionalRequirements, AIRecommendations, ReviewExport];

export function WizardShell() {
  const { state, dispatch } = useProposal();
  const { currentStep } = state;

  function goTo(step: number) {
    if (step >= 0 && step < TOTAL_STEPS) {
      dispatch({ type: "SET_STEP", payload: step });
    }
  }

  function renderStep() {
    const StepComponent = STEP_COMPONENTS[currentStep];
    return <StepComponent />;
  }

  return (
    <div className="flex min-h-screen flex-col bg-background">
      {/* Step indicator */}
      <div className="border-b border-border bg-card px-4 sm:px-8">
        <div className="mx-auto max-w-5xl">
          <StepIndicator
            currentStep={currentStep}
            onStepClick={goTo}
          />
        </div>
      </div>

      {/* Step content */}
      <main className="flex flex-1 flex-col">
        <div className="mx-auto w-full max-w-5xl flex-1 px-4 py-8 sm:px-8">
          {renderStep()}
        </div>
      </main>

      {/* Sticky footer with navigation */}
      <footer className="sticky bottom-0 border-t border-border bg-card/95 backdrop-blur-sm">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3 sm:px-8">
          <Button
            variant="outline"
            onClick={() => goTo(currentStep - 1)}
            disabled={currentStep === 0}
            className="gap-1"
          >
            <ChevronLeft className="h-4 w-4" />
            <span className="hidden sm:inline">Anterior</span>
          </Button>

          <span className="text-sm text-muted-foreground">
            Passo {currentStep + 1} de {TOTAL_STEPS}
          </span>

          <Button
            onClick={() => goTo(currentStep + 1)}
            disabled={currentStep === TOTAL_STEPS - 1}
            className="gap-1"
          >
            <span className="hidden sm:inline">Proximo</span>
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </footer>
    </div>
  );
}
