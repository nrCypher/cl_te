"use client";
import { useState } from "react";
import { useProposal } from "@/hooks/use-proposal";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Plus, X } from "lucide-react";

export function BusinessProcess() {
  const { state, dispatch } = useProposal();
  const bp = state.businessProcess;
  const [asIsInput, setAsIsInput] = useState("");
  const [toBeInput, setToBeInput] = useState("");
  const [changeInput, setChangeInput] = useState("");

  const addAsIs = () => {
    if (!asIsInput.trim()) return;
    dispatch({ type: "UPDATE_BUSINESS_PROCESS", payload: { asIs: [...bp.asIs, { id: `as_${Date.now()}`, description: asIsInput.trim(), order: bp.asIs.length + 1 }] } });
    setAsIsInput("");
  };
  const addToBe = () => {
    if (!toBeInput.trim()) return;
    dispatch({ type: "UPDATE_BUSINESS_PROCESS", payload: { toBe: [...bp.toBe, { id: `tb_${Date.now()}`, description: toBeInput.trim(), order: bp.toBe.length + 1 }] } });
    setToBeInput("");
  };
  const addChange = () => {
    if (!changeInput.trim()) return;
    dispatch({ type: "UPDATE_BUSINESS_PROCESS", payload: { keyChanges: [...bp.keyChanges, changeInput.trim()] } });
    setChangeInput("");
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div><h2 className="text-2xl font-medium">Processos de Negocio</h2><p className="text-muted-foreground mt-1">Documente os processos atuais e futuros.</p></div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader><CardTitle>Processo Atual (AS-IS)</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {bp.asIs.map((step) => (
              <div key={step.id} className="flex items-center gap-2 p-2 rounded-lg bg-muted/50">
                <span className="text-sm font-medium text-muted-foreground w-6">{step.order}.</span>
                <span className="text-sm flex-1">{step.description}</span>
                <button className="text-muted-foreground hover:text-destructive cursor-pointer" onClick={() => dispatch({ type: "UPDATE_BUSINESS_PROCESS", payload: { asIs: bp.asIs.filter((s) => s.id !== step.id).map((s, i) => ({ ...s, order: i + 1 })) } })}><X className="w-4 h-4" /></button>
              </div>
            ))}
            <div className="flex gap-2"><Input value={asIsInput} onChange={(e) => setAsIsInput(e.target.value)} placeholder="Descreva uma etapa atual" onKeyDown={(e) => e.key === "Enter" && addAsIs()} /><Button variant="outline" onClick={addAsIs} className="shrink-0"><Plus className="w-4 h-4" /></Button></div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Processo Futuro (TO-BE)</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {bp.toBe.map((step) => (
              <div key={step.id} className="flex items-center gap-2 p-2 rounded-lg bg-accent/5">
                <span className="text-sm font-medium text-accent w-6">{step.order}.</span>
                <span className="text-sm flex-1">{step.description}</span>
                <button className="text-muted-foreground hover:text-destructive cursor-pointer" onClick={() => dispatch({ type: "UPDATE_BUSINESS_PROCESS", payload: { toBe: bp.toBe.filter((s) => s.id !== step.id).map((s, i) => ({ ...s, order: i + 1 })) } })}><X className="w-4 h-4" /></button>
              </div>
            ))}
            <div className="flex gap-2"><Input value={toBeInput} onChange={(e) => setToBeInput(e.target.value)} placeholder="Descreva uma etapa futura" onKeyDown={(e) => e.key === "Enter" && addToBe()} /><Button variant="outline" onClick={addToBe} className="shrink-0"><Plus className="w-4 h-4" /></Button></div>
          </CardContent>
        </Card>
      </div>
      <Card>
        <CardHeader><CardTitle>Mudancas-Chave</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          {bp.keyChanges.map((change, i) => (
            <div key={i} className="flex items-center gap-2 p-2 rounded-lg bg-muted/50">
              <span className="text-sm flex-1">{change}</span>
              <button className="text-muted-foreground hover:text-destructive cursor-pointer" onClick={() => dispatch({ type: "UPDATE_BUSINESS_PROCESS", payload: { keyChanges: bp.keyChanges.filter((_, j) => j !== i) } })}><X className="w-4 h-4" /></button>
            </div>
          ))}
          <div className="flex gap-2"><Input value={changeInput} onChange={(e) => setChangeInput(e.target.value)} placeholder="Descreva uma mudanca-chave" onKeyDown={(e) => e.key === "Enter" && addChange()} /><Button variant="outline" onClick={addChange} className="shrink-0 gap-1"><Plus className="w-4 h-4" />Adicionar</Button></div>
        </CardContent>
      </Card>
    </div>
  );
}
