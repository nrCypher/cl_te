"use client";
import { useState } from "react";
import { useProposal } from "@/hooks/use-proposal";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { requirementCategories } from "@/lib/default-data";
import { Plus, Trash2 } from "lucide-react";

export function FunctionalRequirements() {
  const { state, dispatch } = useProposal();
  const [category, setCategory] = useState(requirementCategories[0]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [criteria, setCriteria] = useState("");
  const [priority, setPriority] = useState<"Alta" | "Media" | "Baixa">("Media");

  const add = () => {
    if (!title.trim()) return;
    dispatch({ type: "ADD_FUNCTIONAL_REQUIREMENT", payload: { id: `fr_${Date.now()}`, category, title: title.trim(), description: description.trim(), acceptanceCriteria: criteria.trim(), priority } });
    setTitle(""); setDescription(""); setCriteria("");
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div><h2 className="text-2xl font-medium">Requisitos Funcionais</h2><p className="text-muted-foreground mt-1">Defina os requisitos funcionais do sistema.</p></div>
      <Card>
        <CardHeader><CardTitle>Novo Requisito</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2"><Label>Categoria</Label><Select value={category} onValueChange={setCategory}><SelectTrigger><SelectValue /></SelectTrigger><SelectContent>{requirementCategories.map((c) => <SelectItem key={c} value={c}>{c}</SelectItem>)}</SelectContent></Select></div>
            <div className="space-y-2"><Label>Titulo</Label><Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Titulo do requisito" /></div>
            <div className="space-y-2"><Label>Prioridade</Label><Select value={priority} onValueChange={(v) => setPriority(v as "Alta" | "Media" | "Baixa")}><SelectTrigger><SelectValue /></SelectTrigger><SelectContent><SelectItem value="Alta">Alta</SelectItem><SelectItem value="Media">Media</SelectItem><SelectItem value="Baixa">Baixa</SelectItem></SelectContent></Select></div>
          </div>
          <div className="space-y-2"><Label>Descricao</Label><Textarea value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Descreva o requisito" rows={2} /></div>
          <div className="space-y-2"><Label>Criterios de Aceite</Label><Textarea value={criteria} onChange={(e) => setCriteria(e.target.value)} placeholder="Criterios de aceite" rows={2} /></div>
          <Button onClick={add} className="gap-1"><Plus className="w-4 h-4" />Adicionar</Button>
        </CardContent>
      </Card>
      {state.functionalRequirements.length > 0 ? (
        <div className="space-y-3">
          {state.functionalRequirements.map((req) => (
            <Card key={req.id}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2"><Badge variant="outline">{req.category}</Badge><Badge className={req.priority === "Alta" ? "bg-destructive text-destructive-foreground" : req.priority === "Media" ? "bg-accent text-accent-foreground" : "bg-muted text-muted-foreground"}>{req.priority}</Badge></div>
                    <p className="font-medium">{req.title}</p>
                    {req.description && <p className="text-sm text-muted-foreground">{req.description}</p>}
                    {req.acceptanceCriteria && <p className="text-xs text-muted-foreground">Criterios: {req.acceptanceCriteria}</p>}
                  </div>
                  <Button variant="ghost" size="icon" onClick={() => dispatch({ type: "REMOVE_FUNCTIONAL_REQUIREMENT", payload: req.id })}><Trash2 className="w-4 h-4 text-destructive" /></Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : <p className="text-sm text-muted-foreground italic">Nenhum requisito funcional adicionado.</p>}
    </div>
  );
}
