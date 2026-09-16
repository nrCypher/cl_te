"use client"

import { useState } from "react"
import { useProposal } from "@/hooks/use-proposal"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Plus, X } from "lucide-react"

function generateId() {
  return `id_${Date.now()}_${Math.random().toString(36).slice(2)}`
}

export function ScopeDefinition() {
  const { state, dispatch } = useProposal()
  const [inScopeText, setInScopeText] = useState("")
  const [outScopeText, setOutScopeText] = useState("")

  function addItem(list: "inScope" | "outScope") {
    const text = list === "inScope" ? inScopeText.trim() : outScopeText.trim()
    if (!text) return
    dispatch({
      type: "ADD_SCOPE_ITEM",
      payload: {
        list,
        item: { id: generateId(), text },
      },
    })
    if (list === "inScope") {
      setInScopeText("")
    } else {
      setOutScopeText("")
    }
  }

  function removeItem(list: "inScope" | "outScope", id: string) {
    dispatch({
      type: "REMOVE_SCOPE_ITEM",
      payload: { list, id },
    })
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Incluido no Escopo</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            {state.scope.inScope.map((item) => (
              <div
                key={item.id}
                className="flex items-center gap-2 rounded-md border border-border p-3"
              >
                <span className="flex-1 text-sm">{item.text}</span>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => removeItem("inScope", item.id)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>

          <div className="flex gap-2">
            <Input
              value={inScopeText}
              onChange={(e) => setInScopeText(e.target.value)}
              placeholder="Adicionar item ao escopo"
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault()
                  addItem("inScope")
                }
              }}
            />
            <Button onClick={() => addItem("inScope")} size="icon">
              <Plus className="h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Fora do Escopo</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            {state.scope.outScope.map((item) => (
              <div
                key={item.id}
                className="flex items-center gap-2 rounded-md border border-border p-3"
              >
                <span className="flex-1 text-sm">{item.text}</span>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => removeItem("outScope", item.id)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>

          <div className="flex gap-2">
            <Input
              value={outScopeText}
              onChange={(e) => setOutScopeText(e.target.value)}
              placeholder="Adicionar item fora do escopo"
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault()
                  addItem("outScope")
                }
              }}
            />
            <Button onClick={() => addItem("outScope")} size="icon">
              <Plus className="h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
