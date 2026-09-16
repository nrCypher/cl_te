"use client"

import { useState } from "react"
import { useProposal } from "@/hooks/use-proposal"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Plus, X } from "lucide-react"

export function ProjectInfo() {
  const { state, dispatch } = useProposal()
  const { projectInfo } = state
  const [newObjective, setNewObjective] = useState("")

  function handleChange(field: string, value: string) {
    dispatch({
      type: "UPDATE_PROJECT_INFO",
      payload: { [field]: value },
    })
  }

  function addObjective() {
    const text = newObjective.trim()
    if (!text) return
    dispatch({
      type: "UPDATE_PROJECT_INFO",
      payload: { objectives: [...projectInfo.objectives, text] },
    })
    setNewObjective("")
  }

  function removeObjective(index: number) {
    dispatch({
      type: "UPDATE_PROJECT_INFO",
      payload: {
        objectives: projectInfo.objectives.filter((_, i) => i !== index),
      },
    })
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Informacoes do Projeto</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">Nome do Projeto</Label>
              <Input
                id="name"
                value={projectInfo.name}
                onChange={(e) => handleChange("name", e.target.value)}
                placeholder="Nome do projeto"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="client">Cliente</Label>
              <Input
                id="client"
                value={projectInfo.client}
                onChange={(e) => handleChange("client", e.target.value)}
                placeholder="Nome do cliente"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="manager">Gerente do Projeto</Label>
              <Input
                id="manager"
                value={projectInfo.manager}
                onChange={(e) => handleChange("manager", e.target.value)}
                placeholder="Nome do gerente"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="startDate">Data de Inicio</Label>
              <Input
                id="startDate"
                type="date"
                value={projectInfo.startDate}
                onChange={(e) => handleChange("startDate", e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="endDate">Data de Termino</Label>
              <Input
                id="endDate"
                type="date"
                value={projectInfo.endDate}
                onChange={(e) => handleChange("endDate", e.target.value)}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Descricao</Label>
            <Textarea
              id="description"
              value={projectInfo.description}
              onChange={(e) => handleChange("description", e.target.value)}
              placeholder="Descricao detalhada do projeto"
              rows={4}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Objetivos do Projeto</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            {projectInfo.objectives.map((objective, index) => (
              <div
                key={index}
                className="flex items-center gap-2 rounded-md border border-border p-3"
              >
                <span className="flex-1 text-sm">{objective}</span>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => removeObjective(index)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>

          <div className="flex gap-2">
            <Input
              value={newObjective}
              onChange={(e) => setNewObjective(e.target.value)}
              placeholder="Adicionar objetivo"
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault()
                  addObjective()
                }
              }}
            />
            <Button onClick={addObjective} size="icon">
              <Plus className="h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
