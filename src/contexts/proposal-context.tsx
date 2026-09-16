"use client";

import { createContext, useReducer, type ReactNode } from "react";
import type { ProposalState, ProposalAction } from "@/lib/types";
import { initialState } from "@/lib/default-data";

function proposalReducer(state: ProposalState, action: ProposalAction): ProposalState {
  switch (action.type) {
    case "SET_STEP":
      return { ...state, currentStep: action.payload };
    case "UPDATE_PROJECT_INFO":
      return { ...state, projectInfo: { ...state.projectInfo, ...action.payload } };
    case "ADD_SCOPE_ITEM":
      return { ...state, scope: { ...state.scope, [action.payload.list]: [...state.scope[action.payload.list], action.payload.item] } };
    case "REMOVE_SCOPE_ITEM":
      return { ...state, scope: { ...state.scope, [action.payload.list]: state.scope[action.payload.list].filter((item) => item.id !== action.payload.id) } };
    case "UPDATE_STAKEHOLDERS":
      return { ...state, stakeholders: action.payload };
    case "ADD_STAKEHOLDER":
      return { ...state, stakeholders: [...state.stakeholders, action.payload] };
    case "REMOVE_STAKEHOLDER":
      return { ...state, stakeholders: state.stakeholders.filter((s) => s.id !== action.payload) };
    case "UPDATE_BUSINESS_PROCESS":
      return { ...state, businessProcess: { ...state.businessProcess, ...action.payload } };
    case "ADD_FUNCTIONAL_REQUIREMENT":
      return { ...state, functionalRequirements: [...state.functionalRequirements, action.payload] };
    case "REMOVE_FUNCTIONAL_REQUIREMENT":
      return { ...state, functionalRequirements: state.functionalRequirements.filter((r) => r.id !== action.payload) };
    case "UPDATE_FUNCTIONAL_REQUIREMENT":
      return { ...state, functionalRequirements: state.functionalRequirements.map((r) => r.id === action.payload.id ? action.payload : r) };
    case "UPDATE_NFR":
      return { ...state, nonFunctionalRequirements: action.payload };
    case "UPDATE_AI_RECOMMENDATIONS":
      return { ...state, aiRecommendations: { ...state.aiRecommendations, ...action.payload } };
    case "RESET":
      return initialState;
    default:
      return state;
  }
}

export const ProposalContext = createContext<{ state: ProposalState; dispatch: React.Dispatch<ProposalAction> }>({ state: initialState, dispatch: () => {} });

export function ProposalProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(proposalReducer, initialState);
  return <ProposalContext.Provider value={{ state, dispatch }}>{children}</ProposalContext.Provider>;
}
