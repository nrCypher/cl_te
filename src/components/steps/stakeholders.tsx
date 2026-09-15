"use client";
import { useState } from "react";
import { useProposal } from "@/hooks/use-proposal";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { Plus, Trash2 } from "lucide-react";

export function Stakeholders() {
  const { state, dispatch } = useProposal();
  const [name, setName] = useState("");
  const [role, setRole] = useState("");
  const [responsibility, setResponsibility] = useState("");
  const [interest, setInterest] = useState<"Alto" | "Medio" | "Baixo">("Medio");
  const [contact, setContact] = useState("");

  const addStakeholder = () => {
    if (!name.trim() || !role.trim()) return;
    dispatch({ type: "ADD_STAKEHOLDER", payload: { id: `sh_${Date.now()}`, name: name.trim(), role: role.trim(), responsibility: responsibility.trim(), interest, contact: contact.trim() } });
    setName(""); setRole(""); setResponsibility(""); setInterest("Medio"); setContact("");
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div><h2 className="text-2xl font-medium">Stakeholders</h2><p className="text-muted-foreground mt-1">Identifique as partes interessadas do projeto.</p></div>
      <Card>
        <CardHeader><CardTitle>Adicionar Stakeholder</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2"><Label>Nome</Label><Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Nome do stakeholder" /></div>
            <div className="space-y-2"><Label>Papel</Label><Input value={role} onChange={(e) => setRole(e.target.value)} placeholder="Papel no projeto" /></div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2"><Label>Responsabilidade</Label><Input value={responsibility} onChange={(e) => setResponsibility(e.target.value)} placeholder="Responsabilidade" /></div>
            <div className="space-y-2"><Label>Interesse</Label>
              <Select value={interest} onValueChange={(v) => setInterest(v as "Alto" | "Medio" | "Baixo")}><SelectTrigger><SelectValue /></SelectTrigger><SelectContent><SelectItem value="Alto">Alto</SelectItem><SelectItem value="Medio">Medio</SelectItem><SelectItem value="Baixo">Baixo</SelectItem></SelectContent></Select>
            </div>
            <div className="space-y-2"><Label>Contato</Label><Input value={contact} onChange={(e) => setContact(e.target.value)} placeholder="Email" /></div>
          </div>
          <Button onClick={addStakeholder} className="gap-1"><Plus className="w-4 h-4" />Adicionar</Button>
        </CardContent>
      </Card>
      {state.stakeholders.length > 0 ? (
        <div className="space-y-3">
          {state.stakeholders.map((sh) => (
            <Card key={sh.id}>
              <CardContent className="p-4 flex items-center justify-between">
                <div><p className="font-medium">{sh.name}</p><p className="text-sm text-muted-foreground">{sh.role} - {sh.responsibility}</p><p className="text-xs text-muted-foreground">Interesse: {sh.interest} | {sh.contact}</p></div>
                <Button variant="ghost" size="icon" onClick={() => dispatch({ type: "REMOVE_STAKEHOLDER", payload: sh.id })}><Trash2 className="w-4 h-4 text-destructive" /></Button>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : <p className="text-sm text-muted-foreground italic">Nenhum stakeholder adicionado.</p>}
    </div>
  );
}
