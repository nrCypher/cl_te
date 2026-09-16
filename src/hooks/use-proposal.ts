"use client";

import { useContext } from "react";
import { ProposalContext } from "@/contexts/proposal-context";

export function useProposal() {
  const context = useContext(ProposalContext);
  if (!context) {
    throw new Error("useProposal must be used within a ProposalProvider");
  }
  return context;
}
