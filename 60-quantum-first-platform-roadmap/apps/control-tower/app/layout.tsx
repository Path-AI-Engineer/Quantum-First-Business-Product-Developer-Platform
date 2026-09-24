import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "Quantum-First Strategy Control Tower",
  description: "Auditable 1/3/10-year strategy, scenarios, gates, and evidence.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}

