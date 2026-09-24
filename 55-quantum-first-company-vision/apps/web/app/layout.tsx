import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = {
  title: "Venture Evidence Room · Quantum-First",
  description:
    "Trace the evidence. Challenge the assumptions. A local venture decision laboratory.",
};
export default function Layout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
