"use client"

import { useState } from "react"
import { useProposal } from "@/hooks/use-proposal"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Accordion,
  AccordionItem,
  AccordionTrigger,
  AccordionContent,
} from "@/components/ui/accordion"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Separator } from "@/components/ui/separator"
import {
  FileText,
  Download,
  Copy,
  CheckCircle2,
  AlertTriangle,
  Info,
  Lightbulb,
} from "lucide-react"
import { generateAnalysis } from "@/lib/ai-analysis"
import { generateDocument } from "@/lib/document-generator"
import type { ProposalAnalysis, AnalysisInsight } from "@/lib/types"

const insightConfig: Record<
  AnalysisInsight["type"],
  { icon: React.ElementType; color: string; bg: string }
> = {
  success: {
    icon: CheckCircle2,
    color: "text-green-600",
    bg: "bg-green-50 border-green-200",
  },
  warning: {
    icon: AlertTriangle,
    color: "text-yellow-600",
    bg: "bg-yellow-50 border-yellow-200",
  },
  info: {
    icon: Info,
    color: "text-blue-600",
    bg: "bg-blue-50 border-blue-200",
  },
  recommendation: {
    icon: Lightbulb,
    color: "text-purple-600",
    bg: "bg-purple-50 border-purple-200",
  },
}

export function ReviewExport() {
  const { state } = useProposal()
  const [analysis, setAnalysis] = useState<ProposalAnalysis | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [document, setDocument] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [showDocument, setShowDocument] = useState(false)
  const [copied, setCopied] = useState(false)

  async function handleAnalysis() {
    setIsAnalyzing(true)
    try {
      const result = await generateAnalysis(state)
      setAnalysis(result)
    } finally {
      setIsAnalyzing(false)
    }
  }

  async function handleDocument() {
    setIsGenerating(true)
    try {
      const result = await generateDocument(state)
      setDocument(result)
      setShowDocument(true)
    } finally {
      setIsGenerating(false)
    }
  }

  async function handleCopy() {
    if (!document) return
    await navigator.clipboard.writeText(document)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  function handleDownload() {
    if (!document) return
    const blob = new Blob([document], { type: "text/plain;charset=utf-8" })
    const url = URL.createObjectURL(blob)
    const a = window.document.createElement("a")
    a.href = url
    a.download = `proposta-${state.projectInfo.name || "projeto"}.txt`
    window.document.body.appendChild(a)
    a.click()
    window.document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Resumo da Proposta</CardTitle>
        </CardHeader>
        <CardContent>
          <Accordion type="multiple" className="w-full">
            <AccordionItem value="project">
              <AccordionTrigger>Informacoes do Projeto</AccordionTrigger>
              <AccordionContent>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
                  <div>
                    <span className="font-medium">Nome:</span>{" "}
                    {state.projectInfo.name || "-"}
                  </div>
                  <div>
                    <span className="font-medium">Cliente:</span>{" "}
                    {state.projectInfo.client || "-"}
                  </div>
                  <div>
                    <span className="font-medium">Gerente:</span>{" "}
                    {state.projectInfo.manager || "-"}
                  </div>
                  <div>
                    <span className="font-medium">Periodo:</span>{" "}
                    {state.projectInfo.startDate || "-"} a{" "}
                    {state.projectInfo.endDate || "-"}
                  </div>
                </div>
                {state.projectInfo.objectives.length > 0 && (
                  <div className="mt-3">
                    <span className="font-medium text-sm">Objetivos:</span>
                    <ul className="list-disc list-inside text-sm mt-1 space-y-1">
                      {state.projectInfo.objectives.map((obj, i) => (
                        <li key={i}>{obj}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="scope">
              <AccordionTrigger>
                Escopo ({state.scope.inScope.length} incluidos,{" "}
                {state.scope.outScope.length} excluidos)
              </AccordionTrigger>
              <AccordionContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium">Incluido:</span>
                    <ul className="list-disc list-inside mt-1 space-y-1">
                      {state.scope.inScope.map((item) => (
                        <li key={item.id}>{item.text}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <span className="font-medium">Excluido:</span>
                    <ul className="list-disc list-inside mt-1 space-y-1">
                      {state.scope.outScope.map((item) => (
                        <li key={item.id}>{item.text}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="stakeholders">
              <AccordionTrigger>
                Partes Interessadas ({state.stakeholders.length})
              </AccordionTrigger>
              <AccordionContent>
                <div className="space-y-2 text-sm">
                  {state.stakeholders.map((s) => (
                    <div key={s.id} className="flex items-center gap-2">
                      <span className="font-medium">{s.name}</span>
                      <span className="text-muted-foreground">- {s.role}</span>
                      <Badge variant="outline">{s.interest}</Badge>
                    </div>
                  ))}
                </div>
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="process">
              <AccordionTrigger>Processo de Negocio</AccordionTrigger>
              <AccordionContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium">
                      AS-IS ({state.businessProcess.asIs.length} etapas)
                    </span>
                    <ol className="list-decimal list-inside mt-1 space-y-1">
                      {state.businessProcess.asIs.map((s) => (
                        <li key={s.id}>{s.description}</li>
                      ))}
                    </ol>
                  </div>
                  <div>
                    <span className="font-medium">
                      TO-BE ({state.businessProcess.toBe.length} etapas)
                    </span>
                    <ol className="list-decimal list-inside mt-1 space-y-1">
                      {state.businessProcess.toBe.map((s) => (
                        <li key={s.id}>{s.description}</li>
                      ))}
                    </ol>
                  </div>
                </div>
                {state.businessProcess.keyChanges.length > 0 && (
                  <div className="mt-3">
                    <span className="font-medium text-sm">
                      Mudancas Chave:
                    </span>
                    <ul className="list-disc list-inside text-sm mt-1 space-y-1">
                      {state.businessProcess.keyChanges.map((c, i) => (
                        <li key={i}>{c}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="functional">
              <AccordionTrigger>
                Requisitos Funcionais ({state.functionalRequirements.length})
              </AccordionTrigger>
              <AccordionContent>
                <div className="space-y-2 text-sm">
                  {state.functionalRequirements.map((req) => (
                    <div key={req.id} className="flex items-center gap-2">
                      <Badge variant="secondary">{req.category}</Badge>
                      <span>{req.title}</span>
                      <Badge variant="outline">{req.priority}</Badge>
                    </div>
                  ))}
                </div>
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="nfr">
              <AccordionTrigger>
                Requisitos Nao Funcionais (
                {state.nonFunctionalRequirements.length})
              </AccordionTrigger>
              <AccordionContent>
                <div className="space-y-2 text-sm">
                  {state.nonFunctionalRequirements.map((nfr) => (
                    <div key={nfr.id} className="flex items-center gap-2">
                      <Badge variant="secondary">{nfr.category}</Badge>
                      <span>{nfr.description}</span>
                      {nfr.target && (
                        <span className="text-muted-foreground">
                          (Meta: {nfr.target})
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="ai">
              <AccordionTrigger>
                Recomendacoes de IA (
                {state.aiRecommendations.selectedCapabilities.length}{" "}
                capacidades)
              </AccordionTrigger>
              <AccordionContent>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="font-medium">
                      Capacidades selecionadas:
                    </span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {state.aiRecommendations.selectedCapabilities.map(
                        (id) => (
                          <Badge key={id} variant="secondary">
                            {id}
                          </Badge>
                        )
                      )}
                    </div>
                  </div>
                  {state.aiRecommendations.selectedPackage && (
                    <div>
                      <span className="font-medium">Pacote:</span>{" "}
                      {state.aiRecommendations.selectedPackage}
                    </div>
                  )}
                </div>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </CardContent>
      </Card>

      <div className="flex flex-wrap gap-4">
        <Button onClick={handleAnalysis} disabled={isAnalyzing}>
          <FileText className="h-4 w-4" />
          {isAnalyzing ? "Analisando..." : "Gerar Analise"}
        </Button>
        <Button onClick={handleDocument} disabled={isGenerating} variant="outline">
          <FileText className="h-4 w-4" />
          {isGenerating ? "Gerando..." : "Gerar Documento"}
        </Button>
      </div>

      {analysis && (
        <Card>
          <CardHeader>
            <CardTitle>Analise da Proposta</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium">Pontuacao de Completude</span>
                <span className="font-bold">{analysis.completionScore}%</span>
              </div>
              <div className="h-3 w-full rounded-full bg-muted overflow-hidden">
                <div
                  className="h-full rounded-full bg-primary transition-all duration-500"
                  style={{ width: `${analysis.completionScore}%` }}
                />
              </div>
            </div>

            <Separator />

            <div className="space-y-2">
              <h3 className="font-semibold text-sm">Resumo Executivo</h3>
              <p className="text-sm text-muted-foreground">
                {analysis.executiveSummary}
              </p>
            </div>

            <Separator />

            <div className="space-y-3">
              <h3 className="font-semibold text-sm">Insights</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {analysis.insights.map((insight, index) => {
                  const config = insightConfig[insight.type]
                  const Icon = config.icon
                  return (
                    <div
                      key={index}
                      className={`rounded-lg border p-4 space-y-1 ${config.bg}`}
                    >
                      <div className="flex items-center gap-2">
                        <Icon className={`h-4 w-4 ${config.color}`} />
                        <span className="font-medium text-sm">
                          {insight.title}
                        </span>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {insight.description}
                      </p>
                    </div>
                  )
                })}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <Dialog open={showDocument} onOpenChange={setShowDocument}>
        <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Documento da Proposta</DialogTitle>
          </DialogHeader>
          <div className="flex gap-2 mb-4">
            <Button size="sm" variant="outline" onClick={handleCopy}>
              <Copy className="h-4 w-4" />
              {copied ? "Copiado!" : "Copiar"}
            </Button>
            <Button size="sm" variant="outline" onClick={handleDownload}>
              <Download className="h-4 w-4" />
              Baixar
            </Button>
          </div>
          <div className="rounded-md border border-border bg-muted/50 p-4">
            <pre className="whitespace-pre-wrap text-sm font-mono">
              {document}
            </pre>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
