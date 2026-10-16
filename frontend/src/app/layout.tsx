import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Klintec v2.0 | Cotización Dinámica APU & Auditoría IA",
  description:
    "Sistema dinámico de cotización y estructuración de costos unitarios según tipología de infraestructura - Expo Clean Ecuador 2026",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body className="min-h-screen bg-slate-950 text-slate-100 antialiased">
        {children}
      </body>
    </html>
  );
}
