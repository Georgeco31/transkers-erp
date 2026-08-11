import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Transker ERP",
  description: "Gestión operativa de Transker",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="es"><body>{children}</body></html>;
}

