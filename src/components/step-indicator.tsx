"use client";

const STEPS = [
  { label: "Projeto", short: "Projeto" },
  { label: "Escopo", short: "Escopo" },
  { label: "Stakeholders", short: "Stake." },
  { label: "Processos", short: "Proc." },
  { label: "Req. Funcionais", short: "RF" },
  { label: "Req. Nao-Func.", short: "RNF" },
  { label: "IA", short: "IA" },
  { label: "Revisao", short: "Revisao" },
];

export function StepIndicator({ currentStep, onStepClick }: { currentStep: number; onStepClick: (step: number) => void }) {
  return (
    <div className="w-full overflow-x-auto">
      <div className="flex items-center min-w-max px-4 py-4">
        {STEPS.map((step, i) => (
          <div key={i} className="flex items-center">
            <button onClick={() => onStepClick(i)} className={`flex flex-col items-center gap-1.5 group cursor-pointer ${i > currentStep ? "opacity-50" : ""}`}>
              <div className={`w-9 h-9 rounded-full flex items-center justify-center text-sm font-medium transition-all duration-200 border-2 ${
                i < currentStep ? "border-accent bg-accent text-accent-foreground" :
                i === currentStep ? "border-accent text-accent bg-accent/10" :
                "border-border text-muted-foreground bg-muted"
              }`}>{i < currentStep ? "✓" : i + 1}</div>
              <span className={`text-xs font-medium whitespace-nowrap transition-colors duration-200 ${i <= currentStep ? "text-accent" : "text-muted-foreground"}`}>
                <span className="hidden md:inline">{step.label}</span>
                <span className="md:hidden">{step.short}</span>
              </span>
            </button>
            {i < STEPS.length - 1 && <div className={`w-8 lg:w-12 h-0.5 mx-1 transition-colors duration-200 ${i < currentStep ? "bg-accent" : "bg-border"}`} />}
          </div>
        ))}
      </div>
    </div>
  );
}
