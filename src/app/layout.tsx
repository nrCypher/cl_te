import type { Metadata } from "next";
import "./globals.css";
import { ProposalProvider } from "@/contexts/proposal-context";

export const metadata: Metadata = {
  title: "Construtor de Propostas Comerciais",
  description: "Ferramenta profissional para criacao de propostas comerciais de software com recomendacoes inteligentes.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" className="h-full antialiased">
      <body className="min-h-full flex flex-col font-sans">
        <ProposalProvider>{children}</ProposalProvider>
      </body>
    </html>
  );
}
