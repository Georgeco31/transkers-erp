"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Bars3Icon, XMarkIcon } from "@heroicons/react/24/outline";
import { api } from "@/lib/api";

const links = [
  ["Inicio", "/dashboard"], ["Viajes", "/trips"], ["Clientes", "/clients"], ["Choferes", "/drivers"],
  ["Vehículos", "/vehicles"], ["Cobranzas", "/payments"], ["Gastos vehiculares", "/vehicle-expenses"],
  ["Reportes", "/reports/monthly"], ["Configuración", "/settings"],
];

export default function AppShell({ children }: { children: React.ReactNode }) {
  const path = usePathname(); const router = useRouter(); const [open, setOpen] = useState(false); const [user, setUser] = useState("");
  useEffect(() => { api<{ username: string }>("/auth/me").then(x => setUser(x.username)).catch(() => router.replace("/login")); }, [router]);
  async function logout() { await api("/auth/logout", { method: "POST" }); router.replace("/login"); }
  const nav = <><div className="border-b border-white/10 px-6 py-6"><p className="text-xs font-bold uppercase tracking-[.24em] text-emerald-300">Transker</p><p className="mt-1 text-xl font-bold text-white">ERP operativo</p></div><nav className="flex-1 space-y-1 p-3">{links.map(([label, href]) => { const active = path === href || (href !== "/dashboard" && path.startsWith(`${href}/`)); return <Link key={href} onClick={() => setOpen(false)} href={href} className={`block min-h-11 rounded-xl px-3 py-3 text-sm font-semibold transition ${active ? "bg-white text-emerald-900" : "text-slate-200 hover:bg-white/10 hover:text-white"}`}>{label}</Link>; })}</nav><div className="border-t border-white/10 p-4"><p className="mb-2 truncate text-xs text-slate-300">Sesión: {user || "…"}</p><button onClick={logout} className="w-full rounded-xl border border-white/20 px-3 py-2 text-left text-sm font-semibold text-white hover:bg-white/10">Cerrar sesión</button></div></>;
  return <div className="min-h-screen bg-slate-50 md:grid md:grid-cols-[240px_1fr]">
    <aside className="sticky top-0 hidden h-screen flex-col bg-slate-950 md:flex">{nav}</aside>
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-slate-200 bg-white/95 px-4 backdrop-blur md:hidden"><p className="font-bold text-slate-900">Transker ERP</p><button aria-label="Abrir menú" onClick={() => setOpen(true)} className="rounded-lg p-2"><Bars3Icon className="h-6 w-6" /></button></header>
    {open && <div className="fixed inset-0 z-50 md:hidden"><button aria-label="Cerrar menú" className="absolute inset-0 bg-slate-950/60" onClick={() => setOpen(false)} /><aside className="relative flex h-full w-[82%] max-w-xs flex-col bg-slate-950 shadow-2xl"><button aria-label="Cerrar menú" className="absolute right-3 top-3 rounded-lg p-2 text-white" onClick={() => setOpen(false)}><XMarkIcon className="h-6 w-6" /></button>{nav}</aside></div>}
    <main className="min-w-0 p-4 pb-12 sm:p-6 lg:p-8">{children}</main>
  </div>;
}

