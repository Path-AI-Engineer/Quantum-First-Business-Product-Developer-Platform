import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "QDP Reference Lab",
  description: "Executable quantum-ready developer platform reference design",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

