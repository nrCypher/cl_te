"use client";
import { useProposal } from "@/hooks/use-proposal";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from "@/components/ui/accordion";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { aiCapabilities, aiPackages } from "@/lib/default-data";
import { Check } from "lucide-react";

export function AIRecommendations() {
  const { state, dispatch } = useProposal();
  const selected = state.aiRecommendations.selectedCapabilities;

  const toggleCapability = (id: string) => {
    const updated = selected.includes(id) ? selected.filter((c) => c !== id) : [...selected, id];
    dispatch({ type: "UPDATE_AI_RECOMMENDATIONS", payload: { selectedCapabilities: updated } });
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div><h2 className="text-2xl font-medium">Recomendacoes de IA</h2><p className="text-muted-foreground mt-1">Selecione capacidades de IA e um pacote para o projeto.</p></div>
      <Card>
        <CardHeader><CardTitle>Capacidades de IA</CardTitle></CardHeader>
        <CardContent>
          <Accordion type="multiple" className="w-full">
            {aiCapabilities.map((cap) => (
              <AccordionItem key={cap.id} value={cap.id}>
                <AccordionTrigger>
                  <div className="flex items-center gap-3 text-left">
                    <button type="button" onClick={(e) => { e.stopPropagation(); toggleCapability(cap.id); }} className={`w-5 h-5 rounded border-2 flex items-center justify-center shrink-0 cursor-pointer ${selected.includes(cap.id) ? "bg-accent border-accent" : "border-border"}`}>
                      {selected.includes(cap.id) && <Check className="w-3 h-3 text-accent-foreground" />}
                    </button>
                    <span>{cap.name}</span>
                    <Badge variant="outline" className="ml-auto mr-2">{cap.complexity}</Badge>
                  </div>
                </AccordionTrigger>
                <AccordionContent>
                  <p className="text-sm text-muted-foreground mb-2">{cap.description}</p>
                  <p className="text-xs text-muted-foreground">Fase: {cap.phase}</p>
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle>Pacotes de IA</CardTitle></CardHeader>
        <CardContent>
          <RadioGroup value={state.aiRecommendations.selectedPackage || ""} onValueChange={(v) => dispatch({ type: "UPDATE_AI_RECOMMENDATIONS", payload: { selectedPackage: v || null } })}>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {aiPackages.map((pkg) => (
                <div key={pkg.id} className={`p-4 rounded-xl border-2 cursor-pointer transition-colors ${state.aiRecommendations.selectedPackage === pkg.id ? "border-accent bg-accent/5" : "border-border"}`} onClick={() => dispatch({ type: "UPDATE_AI_RECOMMENDATIONS", payload: { selectedPackage: pkg.id } })}>
                  <div className="flex items-center gap-2 mb-2"><RadioGroupItem value={pkg.id} id={pkg.id} /><Label htmlFor={pkg.id} className="font-medium cursor-pointer">{pkg.name}</Label></div>
                  <p className="text-sm text-muted-foreground mb-3">{pkg.description}</p>
                  <p className="text-sm font-medium text-accent mb-2">{pkg.price}</p>
                  <ul className="space-y-1">{pkg.features.map((f) => <li key={f} className="text-xs text-muted-foreground flex items-center gap-1"><Check className="w-3 h-3 text-accent" />{f}</li>)}</ul>
                </div>
              ))}
            </div>
          </RadioGroup>
        </CardContent>
      </Card>
    </div>
  );
}
