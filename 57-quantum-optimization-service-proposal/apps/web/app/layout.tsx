import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Optimization Value Validation Lab",
  description: "Classical-first evidence for optimization opportunities and pilots",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
