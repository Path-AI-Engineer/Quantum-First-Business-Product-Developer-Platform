import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Cryptographic Migration Command Center",
  description: "Synthetic offline post-quantum migration assessment prototype",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
