import type { ProposalState } from "./types";
import { aiCapabilities, aiPackages } from "./default-data";

export function generateDocument(state: ProposalState): string {
  const lines: string[] = [];
  const now = new Date().toLocaleDateString("pt-BR");

  lines.push("# PROPOSTA COMERCIAL DE SOFTWARE");
  lines.push("");
  lines.push(`**Data:** ${now}`);
  lines.push("");

  lines.push("## 1. Informacoes do Projeto");
  lines.push("");
  if (state.projectInfo.name) lines.push(`**Projeto:** ${state.projectInfo.name}`);
  if (state.projectInfo.client) lines.push(`**Cliente:** ${state.projectInfo.client}`);
  if (state.projectInfo.manager) lines.push(`**Gerente do Projeto:** ${state.projectInfo.manager}`);
  if (state.projectInfo.startDate) lines.push(`**Inicio Previsto:** ${state.projectInfo.startDate}`);
  if (state.projectInfo.endDate) lines.push(`**Conclusao Prevista:** ${state.projectInfo.endDate}`);
  lines.push("");
  if (state.projectInfo.description) {
    lines.push("### Descricao");
    lines.push(state.projectInfo.description);
    lines.push("");
  }
  if (state.projectInfo.objectives.length > 0) {
    lines.push("### Objetivos");
    state.projectInfo.objectives.forEach((obj) => lines.push(`- ${obj}`));
    lines.push("");
  }

  lines.push("## 2. Escopo do Projeto");
  lines.push("");
  if (state.scope.inScope.length > 0) {
    lines.push("### Incluido no Escopo");
    state.scope.inScope.forEach((item) => lines.push(`- ${item.text}`));
    lines.push("");
  }
  if (state.scope.outScope.length > 0) {
    lines.push("### Fora do Escopo");
    state.scope.outScope.forEach((item) => lines.push(`- ${item.text}`));
    lines.push("");
  }

  if (state.stakeholders.length > 0) {
    lines.push("## 3. Stakeholders");
    lines.push("");
    lines.push("| Nome | Papel | Responsabilidade | Interesse |");
    lines.push("|------|-------|------------------|-----------|");
    state.stakeholders.forEach((sh) => lines.push(`| ${sh.name} | ${sh.role} | ${sh.responsibility} | ${sh.interest} |`));
    lines.push("");
  }

  lines.push("## 4. Processos de Negocio");
  lines.push("");
  if (state.businessProcess.asIs.length > 0) {
    lines.push("### Processo Atual (AS-IS)");
    state.businessProcess.asIs.forEach((step) => lines.push(`${step.order}. ${step.description}`));
    lines.push("");
  }
  if (state.businessProcess.toBe.length > 0) {
    lines.push("### Processo Futuro (TO-BE)");
    state.businessProcess.toBe.forEach((step) => lines.push(`${step.order}. ${step.description}`));
    lines.push("");
  }
  if (state.businessProcess.keyChanges.length > 0) {
    lines.push("### Mudancas-Chave");
    state.businessProcess.keyChanges.forEach((change) => lines.push(`- ${change}`));
    lines.push("");
  }

  if (state.functionalRequirements.length > 0) {
    lines.push("## 5. Requisitos Funcionais");
    lines.push("");
    lines.push("| # | Categoria | Titulo | Prioridade |");
    lines.push("|---|-----------|--------|------------|");
    state.functionalRequirements.forEach((req, i) => lines.push(`| ${i + 1} | ${req.category} | ${req.title} | ${req.priority} |`));
    lines.push("");
    state.functionalRequirements.forEach((req, i) => {
      lines.push(`### RF${i + 1}: ${req.title}`);
      if (req.description) lines.push(req.description);
      if (req.acceptanceCriteria) lines.push(`**Criterios de Aceite:** ${req.acceptanceCriteria}`);
      lines.push("");
    });
  }

  if (state.nonFunctionalRequirements.length > 0) {
    lines.push("## 6. Requisitos Nao-Funcionais");
    lines.push("");
    lines.push("| Categoria | Descricao | Metrica | Meta |");
    lines.push("|-----------|-----------|---------|------|");
    state.nonFunctionalRequirements.forEach((req) => lines.push(`| ${req.category} | ${req.description} | ${req.metric} | ${req.target} |`));
    lines.push("");
  }

  if (state.aiRecommendations.selectedCapabilities.length > 0 || state.aiRecommendations.selectedPackage) {
    lines.push("## 7. Recomendacoes de Inteligencia Artificial");
    lines.push("");
    if (state.aiRecommendations.selectedCapabilities.length > 0) {
      lines.push("### Capacidades Selecionadas");
      state.aiRecommendations.selectedCapabilities.forEach((capId) => {
        const cap = aiCapabilities.find((c) => c.id === capId);
        if (cap) {
          lines.push(`- **${cap.name}** (${cap.complexity}) - ${cap.phase}`);
          lines.push(`  ${cap.description}`);
        }
      });
      lines.push("");
    }
    if (state.aiRecommendations.selectedPackage) {
      const pkg = aiPackages.find((p) => p.id === state.aiRecommendations.selectedPackage);
      if (pkg) {
        lines.push("### Pacote Selecionado");
        lines.push(`**${pkg.name}** - ${pkg.description}`);
        lines.push(`**Investimento:** ${pkg.price}`);
        lines.push("");
        lines.push("**Funcionalidades incluidas:**");
        pkg.features.forEach((f) => lines.push(`- ${f}`));
        lines.push("");
      }
    }
  }

  lines.push("---");
  lines.push(`*Documento gerado automaticamente em ${now}*`);
  return lines.join("\n");
}
