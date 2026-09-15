import type {
  ScopeItem,
  Stakeholder,
  ProcessStep,
  FunctionalRequirement,
  NonFunctionalRequirement,
  AICapability,
  AIPackage,
  ProposalState,
} from "./types";

let counter = 0;
export function uid(): string {
  counter += 1;
  return `id-${Date.now()}-${counter}`;
}

export const defaultScopeIn: ScopeItem[] = [
  {
    id: uid(),
    text: "Desenvolvimento do modulo de ordens de servico com fluxo completo de criacao, atribuicao, execucao e encerramento",
  },
  {
    id: uid(),
    text: "Integracao com sistema ERP existente para sincronizacao de dados de ativos, custos e estoque",
  },
  {
    id: uid(),
    text: "Painel de KPIs de manutencao com indicadores como MTBF, MTTR, disponibilidade e backlog",
  },
  {
    id: uid(),
    text: "Aplicativo movel para tecnicos de campo com acesso offline e sincronizacao automatica",
  },
  {
    id: uid(),
    text: "Modulo de gestao de inventario de pecas de reposicao com controle de estoque minimo e maximo",
  },
];

export const defaultScopeOut: ScopeItem[] = [
  {
    id: uid(),
    text: "Migracao de dados historicos anteriores a 2020 do sistema legado",
  },
  {
    id: uid(),
    text: "Desenvolvimento de hardware IoT customizado para monitoramento de equipamentos",
  },
  {
    id: uid(),
    text: "Treinamento presencial nas unidades operacionais da empresa",
  },
  {
    id: uid(),
    text: "Suporte pos-implantacao e manutencao corretiva do sistema apos periodo de garantia",
  },
];

export const defaultStakeholders: Stakeholder[] = [
  {
    id: uid(),
    name: "Carlos Mendes",
    role: "Diretor de Operacoes",
    responsibility:
      "Aprovacao final do projeto e alinhamento estrategico com objetivos organizacionais",
    interest: "Alto",
    contact: "carlos.mendes@empresa.com.br",
  },
  {
    id: uid(),
    name: "Ana Rodrigues",
    role: "Gerente de Manutencao",
    responsibility:
      "Definicao de requisitos operacionais e validacao dos fluxos de trabalho de manutencao",
    interest: "Alto",
    contact: "ana.rodrigues@empresa.com.br",
  },
  {
    id: uid(),
    name: "Felipe Santos",
    role: "Coordenador de TI",
    responsibility:
      "Acompanhamento tecnico da integracao, infraestrutura e seguranca da informacao",
    interest: "Medio",
    contact: "felipe.santos@empresa.com.br",
  },
];

export const defaultAsIs: ProcessStep[] = [
  {
    id: uid(),
    description:
      "Controle de ordens de servico realizado manualmente em planilhas Excel com risco de perda de dados e duplicidade",
    order: 1,
  },
  {
    id: uid(),
    description:
      "Comunicacao entre equipes de manutencao feita por telefone e e-mail sem rastreabilidade ou historico centralizado",
    order: 2,
  },
  {
    id: uid(),
    description:
      "Gestao de estoque de pecas em sistema legado desatualizado sem integracao com compras ou manutencao",
    order: 3,
  },
  {
    id: uid(),
    description:
      "Relatorios gerenciais de manutencao elaborados mensalmente de forma manual com dados frequentemente inconsistentes",
    order: 4,
  },
];

export const defaultToBe: ProcessStep[] = [
  {
    id: uid(),
    description:
      "Ordens de servico digitais com fluxo automatizado de criacao, atribuicao, acompanhamento e encerramento no CMMS",
    order: 1,
  },
  {
    id: uid(),
    description:
      "Notificacoes em tempo real via aplicativo movel com registro fotografico e assinatura digital dos tecnicos",
    order: 2,
  },
  {
    id: uid(),
    description:
      "Estoque integrado ao CMMS e ERP com previsao de demanda e alertas automaticos de reposicao",
    order: 3,
  },
  {
    id: uid(),
    description:
      "Dashboards de KPIs em tempo real com visualizacao de MTBF, MTTR, custos e disponibilidade dos ativos",
    order: 4,
  },
];

export const defaultKeyChanges: string[] = [
  "Transicao de processos manuais baseados em planilhas para fluxos digitais automatizados no CMMS",
  "Adocao de aplicativo movel para equipes de campo eliminando formularios em papel",
  "Implementacao de dashboards em tempo real substituindo relatorios mensais manuais",
];

export const defaultFunctionalRequirements: FunctionalRequirement[] = [
  {
    id: uid(),
    category: "Ordens de Servico",
    title: "Criacao e gestao de ordens de servico",
    description:
      "O sistema deve permitir criar, editar, atribuir e encerrar ordens de servico com campos configuracveis, anexos e historico completo de alteracoes",
    acceptanceCriteria:
      "Usuario cria OS com todos os campos obrigatorios, atribui a um tecnico e acompanha o status ate o encerramento com registro de tempo e materiais",
    priority: "Alta",
  },
  {
    id: uid(),
    category: "Integracao",
    title: "Integracao bidirecional com ERP",
    description:
      "O sistema deve sincronizar dados de ativos, centros de custo, estoque e ordens de compra com o ERP existente via API REST",
    acceptanceCriteria:
      "Dados de ativos e estoque sao sincronizados automaticamente a cada 15 minutos com log de erros e mecanismo de retry",
    priority: "Alta",
  },
  {
    id: uid(),
    category: "Relatorios",
    title: "Painel de indicadores de manutencao",
    description:
      "O sistema deve apresentar dashboard com KPIs como MTBF, MTTR, disponibilidade, backlog e custos de manutencao por ativo e periodo",
    acceptanceCriteria:
      "Dashboard exibe todos os KPIs definidos com filtros por periodo, unidade e tipo de equipamento, atualizando em tempo real",
    priority: "Media",
  },
];

export const defaultNonFunctionalRequirements: NonFunctionalRequirement[] = [
  {
    id: uid(),
    category: "Performance",
    description:
      "O sistema deve responder a consultas e operacoes dentro de limites aceitaveis de tempo",
    metric: "Tempo de resposta",
    target: "95% das requisicoes com tempo de resposta inferior a 2 segundos",
  },
  {
    id: uid(),
    category: "Disponibilidade",
    description:
      "O sistema deve manter alta disponibilidade para suportar operacoes 24/7",
    metric: "Uptime",
    target: "Disponibilidade minima de 99,5% mensal excluindo janelas de manutencao programada",
  },
  {
    id: uid(),
    category: "Seguranca",
    description:
      "O sistema deve proteger dados sensiveis e garantir controle de acesso adequado",
    metric: "Conformidade",
    target: "Autenticacao multifator, criptografia AES-256 em repouso e TLS 1.3 em transito, auditoria completa de acessos",
  },
  {
    id: uid(),
    category: "Escalabilidade",
    description:
      "O sistema deve suportar crescimento no volume de usuarios e dados sem degradacao",
    metric: "Capacidade",
    target: "Suportar ate 500 usuarios simultaneos e 1 milhao de ordens de servico sem degradacao perceptivel",
  },
  {
    id: uid(),
    category: "Usabilidade",
    description:
      "O sistema deve ser intuitivo e acessivel para usuarios com diferentes niveis de experiencia tecnica",
    metric: "Satisfacao do usuario",
    target: "Score SUS (System Usability Scale) acima de 75 pontos em avaliacao com usuarios finais",
  },
];

export const aiCapabilities: AICapability[] = [
  {
    id: uid(),
    name: "Manutencao Preditiva",
    description:
      "Modelos de machine learning para prever falhas em equipamentos com base em dados historicos e sensores, reduzindo paradas nao programadas",
    complexity: "Alta",
    phase: "Fase 2",
  },
  {
    id: uid(),
    name: "Deteccao de Anomalias",
    description:
      "Algoritmos de deteccao de anomalias em tempo real para identificar comportamentos atipicos em equipamentos criticos antes da falha",
    complexity: "Media",
    phase: "Fase 2",
  },
  {
    id: uid(),
    name: "NLP para Ordens de Servico",
    description:
      "Processamento de linguagem natural para classificacao automatica de ordens de servico, extracao de informacoes e sugestao de solucoes com base no historico",
    complexity: "Media",
    phase: "Fase 1",
  },
  {
    id: uid(),
    name: "Previsao de Demanda de Pecas",
    description:
      "Modelos de forecasting para prever necessidade de pecas de reposicao com base em padroes de consumo e planos de manutencao",
    complexity: "Media",
    phase: "Fase 2",
  },
  {
    id: uid(),
    name: "Otimizacao de Recursos",
    description:
      "Algoritmos de otimizacao para alocacao inteligente de tecnicos e equipes considerando habilidades, localizacao e prioridade das ordens",
    complexity: "Alta",
    phase: "Fase 3",
  },
  {
    id: uid(),
    name: "Reconhecimento de Imagem",
    description:
      "Visao computacional para identificacao de defeitos visuais em equipamentos a partir de fotos registradas pelos tecnicos em campo",
    complexity: "Alta",
    phase: "Fase 3",
  },
];

export const aiPackages: AIPackage[] = [
  {
    id: uid(),
    name: "Essencial",
    description:
      "Pacote inicial com capacidades fundamentais de IA para otimizacao basica dos processos de manutencao",
    features: [
      "NLP para classificacao automatica de ordens de servico",
      "Alertas inteligentes baseados em regras e tendencias simples",
      "Relatorios com insights automatizados de manutencao",
    ],
    price: "R$ 45.000/mes",
  },
  {
    id: uid(),
    name: "Avancado",
    description:
      "Pacote intermediario com modelos preditivos e deteccao de anomalias para prevencao proativa de falhas",
    features: [
      "Todas as funcionalidades do pacote Essencial",
      "Manutencao preditiva com modelos de machine learning",
      "Deteccao de anomalias em tempo real",
      "Previsao de demanda de pecas de reposicao",
    ],
    price: "R$ 85.000/mes",
  },
  {
    id: uid(),
    name: "Enterprise",
    description:
      "Pacote completo com todas as capacidades de IA incluindo otimizacao avancada e visao computacional",
    features: [
      "Todas as funcionalidades do pacote Avancado",
      "Otimizacao inteligente de alocacao de recursos e equipes",
      "Reconhecimento de imagem para inspecao visual automatizada",
      "Modelos customizados treinados com dados especificos da operacao",
      "Suporte dedicado de cientistas de dados",
    ],
    price: "R$ 150.000/mes",
  },
];

export const requirementCategories: string[] = [
  "Ordens de Servico",
  "Gestao de Ativos",
  "Integracao",
  "Relatorios",
  "Mobilidade",
  "Estoque",
  "Planejamento",
];

export const nfrCategories: string[] = [
  "Performance",
  "Disponibilidade",
  "Seguranca",
  "Escalabilidade",
  "Usabilidade",
  "Manutenibilidade",
  "Compatibilidade",
];

export const initialState: ProposalState = {
  currentStep: 0,
  projectInfo: {
    name: "",
    client: "",
    manager: "",
    startDate: "",
    endDate: "",
    description: "",
    objectives: [],
  },
  scope: {
    inScope: defaultScopeIn,
    outScope: defaultScopeOut,
  },
  stakeholders: defaultStakeholders,
  businessProcess: {
    asIs: defaultAsIs,
    toBe: defaultToBe,
    keyChanges: defaultKeyChanges,
  },
  functionalRequirements: defaultFunctionalRequirements,
  nonFunctionalRequirements: defaultNonFunctionalRequirements,
  aiRecommendations: {
    selectedCapabilities: [],
    selectedPackage: null,
  },
};
