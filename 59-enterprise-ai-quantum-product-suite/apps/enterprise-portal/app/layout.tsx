import type { Metadata } from "next";
import "./styles.css";
import "./responsive.css";

export const metadata: Metadata = {
  title: "Enterprise Quantum Intelligence Suite",
  description: "Synthetic enterprise portfolio and governance reference portal",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
