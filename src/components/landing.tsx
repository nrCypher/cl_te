"use client";

import Link from "next/link";
import { FileText, Users, BarChart3, Lightbulb, ArrowRight, CheckCircle2 } from "lucide-react";

const features = [
  { icon: FileText, title: "Escopo Estruturado", desc: "Defina claramente o que esta incluido e excluido do projeto." },
  { icon: Users, title: "Matriz de Stakeholders", desc: "Identifique partes interessadas, papeis e niveis de envolvimento." },
  { icon: BarChart3, title: "Requisitos Completos", desc: "Capture requisitos funcionais e nao-funcionais com prioridades." },
  { icon: Lightbulb, title: "Recomendacoes de IA", desc: "Sugestoes inteligentes de capacidades de IA para seu projeto." },
];

const steps = [
  "Informacoes do Projeto", "Definicao de Escopo", "Stakeholders", "Processos de Negocio",
  "Requisitos Funcionais e Nao-Funcionais", "Recomendacoes de IA", "Revisao e Exportacao",
];

export function Landing() {
  return (
    <div className="flex flex-col min-h-screen">
      <header className="border-b bg-card">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
            <FileText className="w-4 h-4 text-primary-foreground" aria-hidden="true" />
          </div>
          <span className="font-semibold text-lg">PropostaBuilder</span>
        </div>
      </header>
      <main className="flex-1 flex flex-col items-center justify-center px-6 py-20">
        <div className="max-w-3xl mx-auto text-center space-y-8">
          <h1 className="text-4xl md:text-5xl font-semibold tracking-tight leading-tight font-serif">Construtor de Propostas Comerciais</h1>
          <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            Crie propostas profissionais de software de forma guiada e inteligente. Organize escopo, requisitos e recomendacoes em um documento completo.
          </p>
          <Link href="/proposta">
            <button className="inline-flex items-center justify-center font-medium bg-accent text-accent-foreground shadow-sm hover:brightness-110 hover:-translate-y-0.5 h-12 rounded-lg px-8 text-base gap-2 mt-4 transition-all duration-200 cursor-pointer">
              Nova Proposta <ArrowRight className="w-5 h-5" aria-hidden="true" />
            </button>
          </Link>
        </div>
        <div className="max-w-5xl mx-auto mt-20 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 w-full">
          {features.map((f) => (
            <div key={f.title} className="flex flex-col items-start p-6 rounded-xl border bg-card hover:shadow-md transition-shadow duration-200">
              <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center mb-4">
                <f.icon className="w-5 h-5 text-accent" aria-hidden="true" />
              </div>
              <h3 className="font-medium text-base mb-2">{f.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
        <div className="max-w-3xl mx-auto mt-20 w-full">
          <h2 className="text-2xl font-medium text-center mb-8">Processo Simplificado</h2>
          <div className="space-y-4">
            {steps.map((step, i) => (
              <div key={step} className="flex items-center gap-4">
                <div className="w-8 h-8 rounded-full bg-accent/10 flex items-center justify-center shrink-0">
                  <CheckCircle2 className="w-4 h-4 text-accent" aria-hidden="true" />
                </div>
                <span className="text-sm font-medium">{i + 1}. {step}</span>
              </div>
            ))}
          </div>
        </div>
      </main>
      <footer className="border-t bg-card py-6">
        <div className="max-w-6xl mx-auto px-6 text-center text-sm text-muted-foreground">PropostaBuilder - Ferramenta de criacao de propostas comerciais</div>
      </footer>
    </div>
  );
}
