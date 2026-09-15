export interface ScopeItem {
  id: string;
  text: string;
}

export interface Stakeholder {
  id: string;
  name: string;
  role: string;
  responsibility: string;
  interest: "Alto" | "Medio" | "Baixo";
  contact: string;
}

export interface ProcessStep {
  id: string;
  description: string;
  order: number;
}

export interface FunctionalRequirement {
  id: string;
  category: string;
  title: string;
  description: string;
  acceptanceCriteria: string;
  priority: "Alta" | "Media" | "Baixa";
}

export interface NonFunctionalRequirement {
  id: string;
  category: string;
  description: string;
  metric: string;
  target: string;
}

export interface AICapability {
  id: string;
  name: string;
  description: string;
  complexity: "Baixa" | "Media" | "Alta";
  phase: string;
}

export interface AIPackage {
  id: string;
  name: string;
  description: string;
  features: string[];
  price: string;
}

export interface AnalysisInsight {
  type: "success" | "warning" | "info" | "recommendation";
  title: string;
  description: string;
}

export interface ProposalAnalysis {
  executiveSummary: string;
  insights: AnalysisInsight[];
  completionScore: number;
}

export interface ProjectInfo {
  name: string;
  client: string;
  manager: string;
  startDate: string;
  endDate: string;
  description: string;
  objectives: string[];
}

export interface BusinessProcess {
  asIs: ProcessStep[];
  toBe: ProcessStep[];
  keyChanges: string[];
}

export interface ProposalState {
  currentStep: number;
  projectInfo: ProjectInfo;
  scope: {
    inScope: ScopeItem[];
    outScope: ScopeItem[];
  };
  stakeholders: Stakeholder[];
  businessProcess: BusinessProcess;
  functionalRequirements: FunctionalRequirement[];
  nonFunctionalRequirements: NonFunctionalRequirement[];
  aiRecommendations: {
    selectedCapabilities: string[];
    selectedPackage: string | null;
  };
}

export type ProposalAction =
  | { type: "SET_STEP"; payload: number }
  | { type: "UPDATE_PROJECT_INFO"; payload: Partial<ProjectInfo> }
  | { type: "ADD_SCOPE_ITEM"; payload: { list: "inScope" | "outScope"; item: ScopeItem } }
  | { type: "REMOVE_SCOPE_ITEM"; payload: { list: "inScope" | "outScope"; id: string } }
  | { type: "UPDATE_STAKEHOLDERS"; payload: Stakeholder[] }
  | { type: "ADD_STAKEHOLDER"; payload: Stakeholder }
  | { type: "REMOVE_STAKEHOLDER"; payload: string }
  | { type: "UPDATE_BUSINESS_PROCESS"; payload: Partial<BusinessProcess> }
  | { type: "ADD_FUNCTIONAL_REQUIREMENT"; payload: FunctionalRequirement }
  | { type: "REMOVE_FUNCTIONAL_REQUIREMENT"; payload: string }
  | { type: "UPDATE_FUNCTIONAL_REQUIREMENT"; payload: FunctionalRequirement }
  | { type: "UPDATE_NFR"; payload: NonFunctionalRequirement[] }
  | { type: "UPDATE_AI_RECOMMENDATIONS"; payload: { selectedCapabilities?: string[]; selectedPackage?: string | null } }
  | { type: "RESET" };
