import type { ProposalState, ProposalAnalysis, AnalysisInsight } from "./types";

export function generateAnalysis(state: ProposalState): ProposalAnalysis {
  const insights: AnalysisInsight[] = [];
  let completedSections = 0;
  const totalSections = 7;

  const pi = state.projectInfo;
  if (pi.name && pi.client && pi.description) {
    completedSections++;
    insights.push({ type: "success", title: "Informacoes do projeto completas", description: "Os dados basicos do projeto estao preenchidos adequadamente." });
  } else {
    const missing = [];
    if (!pi.name) missing.push("nome do projeto");
    if (!pi.client) missing.push("cliente");
    if (!pi.description) missing.push("descricao");
    insights.push({ type: "warning", title: "Informacoes do projeto incompletas", description: `Campos pendentes: ${missing.join(", ")}.` });
  }

  if (pi.objectives.length === 0) {
    insights.push({ type: "recommendation", title: "Adicione objetivos do projeto", description: "Objetivos claros ajudam a alinhar expectativas e medir o sucesso do projeto." });
  } else if (pi.objectives.length >= 3) {
    insights.push({ type: "success", title: `${pi.objectives.length} objetivos definidos`, description: "Boa cobertura de objetivos para o projeto." });
  }

  if (state.scope.inScope.length > 0) {
    completedSections++;
    insights.push({ type: "success", title: `Escopo definido com ${state.scope.inScope.length} itens incluidos`, description: `${state.scope.outScope.length} itens explicitamente excluidos.` });
  }
  if (state.scope.outScope.length === 0 && state.scope.inScope.length > 0) {
    insights.push({ type: "recommendation", title: "Defina exclusoes de escopo", description: "Definir o que esta fora do escopo ajuda a prevenir scope creep e alinhar expectativas." });
  }

  if (state.stakeholders.length > 0) {
    completedSections++;
    const highInterest = state.stakeholders.filter((s) => s.interest === "Alto").length;
    insights.push({ type: "info", title: `${state.stakeholders.length} stakeholders identificados`, description: `${highInterest} com alto nivel de interesse no projeto.` });
  } else {
    insights.push({ type: "warning", title: "Nenhum stakeholder identificado", description: "E importante identificar as partes interessadas para garantir alinhamento." });
  }

  if (state.businessProcess.asIs.length > 0 && state.businessProcess.toBe.length > 0) {
    completedSections++;
    insights.push({ type: "success", title: "Processos AS-IS e TO-BE documentados", description: `${state.businessProcess.asIs.length} etapas atuais vs ${state.businessProcess.toBe.length} etapas futuras.` });
  }
  if (state.businessProcess.keyChanges.length > 0) {
    insights.push({ type: "info", title: `${state.businessProcess.keyChanges.length} mudancas-chave identificadas`, description: "Transformacoes bem documentadas facilitam a comunicacao com stakeholders." });
  }

  if (state.functionalRequirements.length > 0) {
    completedSections++;
    const highPriority = state.functionalRequirements.filter((r) => r.priority === "Alta").length;
    const categories = new Set(state.functionalRequirements.map((r) => r.category));
    insights.push({ type: "success", title: `${state.functionalRequirements.length} requisitos funcionais em ${categories.size} categorias`, description: `${highPriority} requisitos de alta prioridade identificados.` });
    if (highPriority > state.functionalRequirements.length * 0.7) {
      insights.push({ type: "warning", title: "Muitos requisitos de alta prioridade", description: "Considere revisar as prioridades. Quando tudo e prioridade alta, nada e verdadeiramente prioritario." });
    }
  } else {
    insights.push({ type: "warning", title: "Nenhum requisito funcional definido", description: "Requisitos funcionais sao essenciais para a proposta." });
  }

  if (state.nonFunctionalRequirements.length > 0) {
    completedSections++;
    const nfrCats = new Set(state.nonFunctionalRequirements.map((r) => r.category));
    insights.push({ type: "success", title: `${state.nonFunctionalRequirements.length} requisitos nao-funcionais`, description: `Categorias cobertas: ${Array.from(nfrCats).join(", ")}.` });
    const important = ["Seguranca", "Performance", "Disponibilidade"];
    const missing = important.filter((cat) => !nfrCats.has(cat));
    if (missing.length > 0) {
      insights.push({ type: "recommendation", title: "Categorias NFR importantes nao cobertas", description: `Considere adicionar requisitos de: ${missing.join(", ")}.` });
    }
  } else {
    insights.push({ type: "warning", title: "Nenhum requisito nao-funcional", description: "Requisitos de qualidade sao fundamentais para o sucesso do projeto." });
  }

  if (state.aiRecommendations.selectedCapabilities.length > 0 || state.aiRecommendations.selectedPackage) {
    completedSections++;
    if (state.aiRecommendations.selectedPackage) {
      insights.push({ type: "info", title: "Pacote de IA selecionado", description: `Pacote ${state.aiRecommendations.selectedPackage} escolhido com ${state.aiRecommendations.selectedCapabilities.length} capacidades.` });
    }
  } else {
    insights.push({ type: "info", title: "Secao de IA opcional", description: "Nenhuma capacidade de IA selecionada. Esta secao e opcional." });
  }

  const completionScore = Math.round((completedSections / totalSections) * 100);
  const clientName = pi.client || "o cliente";
  const projectName = pi.name || "o projeto";
  const executiveSummary = `A proposta para ${projectName} destinada a ${clientName} apresenta ${completionScore}% de completude. ${state.functionalRequirements.length > 0 ? `Foram identificados ${state.functionalRequirements.length} requisitos funcionais` : "Requisitos funcionais ainda precisam ser definidos"}${state.nonFunctionalRequirements.length > 0 ? ` e ${state.nonFunctionalRequirements.length} requisitos nao-funcionais` : ""}. ${state.stakeholders.length > 0 ? `O projeto conta com ${state.stakeholders.length} stakeholders identificados.` : "Stakeholders ainda precisam ser identificados."} ${state.businessProcess.asIs.length > 0 ? `A analise de processos documenta ${state.businessProcess.asIs.length} etapas atuais e ${state.businessProcess.toBe.length} etapas do estado futuro.` : ""}`;

  return { executiveSummary, insights, completionScore };
}
