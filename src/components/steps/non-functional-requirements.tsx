"use client"

import { useState } from "react"
import { useProposal } from "@/hooks/use-proposal"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@/components/ui/select"
import { Separator } from "@/components/ui/separator"
import { Plus, Trash2 } from "lucide-react"
import { nfrCategories } from "@/lib/default-data"
import type { NonFunctionalRequirement } from "@/lib/types"

function generateId() {
  return `id_${Date.now()}_${Math.random().toString(36).slice(2)}`
}

const emptyForm = {
  category: "",
  description: "",
  metric: "",
  target: "",
}

export function NonFunctionalRequirements() {
  const { state, dispatch } = useProposal()
  const [form, setForm] = useState(emptyForm)

  function addNfr() {
    if (!form.category || !form.description.trim()) return
    const nfr: NonFunctionalRequirement = {
      id: generateId(),
      category: form.category,
      description: form.description.trim(),
      metric: form.metric.trim(),
      target: form.target.trim(),
    }
    dispatch({
      type: "UPDATE_NFR",
      payload: [...state.nonFunctionalRequirements, nfr],
    })
    setForm(emptyForm)
  }

  function removeNfr(id: string) {
    dispatch({
      type: "UPDATE_NFR",
      payload: state.nonFunctionalRequirements.filter((n) => n.id !== id),
    })
  }

  const grouped = state.nonFunctionalRequirements.reduce<
    Record<string, NonFunctionalRequirement[]>
  >((acc, nfr) => {
    if (!acc[nfr.category]) acc[nfr.category] = []
    acc[nfr.category].push(nfr)
    return acc
  }, {})

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Requisitos Nao Funcionais</CardTitle>
        </CardHeader>
        <CardContent>
          {state.nonFunctionalRequirements.length === 0 ? (
            <p className="text-sm text-muted-foreground py-4 text-center">
              Nenhum requisito nao funcional adicionado.
            </p>
          ) : (
            <div className="space-y-6">
              {Object.entries(grouped).map(([category, nfrs]) => (
                <div key={category} className="space-y-2">
                  <h3 className="text-sm font-semibold flex items-center gap-2">
                    <Badge variant="secondary">{category}</Badge>
                  </h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-border">
                          <th className="text-left py-2 pr-4 font-medium">
                            Descricao
                          </th>
                          <th className="text-left py-2 pr-4 font-medium">
                            Metrica
                          </th>
                          <th className="text-left py-2 pr-4 font-medium">
                            Meta
                          </th>
                          <th className="w-10" />
                        </tr>
                      </thead>
                      <tbody>
                        {nfrs.map((nfr) => (
                          <tr key={nfr.id} className="border-b border-border">
                            <td className="py-2 pr-4">{nfr.description}</td>
                            <td className="py-2 pr-4">{nfr.metric}</td>
                            <td className="py-2 pr-4">{nfr.target}</td>
                            <td className="py-2">
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => removeNfr(nfr.id)}
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Adicionar Requisito Nao Funcional</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="nfr-category">Categoria</Label>
              <Select
                value={form.category}
                onValueChange={(value) =>
                  setForm({ ...form, category: value })
                }
              >
                <SelectTrigger id="nfr-category">
                  <SelectValue placeholder="Selecionar categoria" />
                </SelectTrigger>
                <SelectContent>
                  {nfrCategories.map((cat) => (
                    <SelectItem key={cat} value={cat}>
                      {cat}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="nfr-metric">Metrica</Label>
              <Input
                id="nfr-metric"
                value={form.metric}
                onChange={(e) => setForm({ ...form, metric: e.target.value })}
                placeholder="Ex: Tempo de resposta"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="nfr-desc">Descricao</Label>
            <Input
              id="nfr-desc"
              value={form.description}
              onChange={(e) =>
                setForm({ ...form, description: e.target.value })
              }
              placeholder="Descricao do requisito"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="nfr-target">Meta</Label>
            <Input
              id="nfr-target"
              value={form.target}
              onChange={(e) => setForm({ ...form, target: e.target.value })}
              placeholder="Ex: < 200ms"
            />
          </div>

          <Separator />

          <Button onClick={addNfr}>
            <Plus className="h-4 w-4" />
            Adicionar Requisito
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
