"use client";
import Link from"next/link";import{usePathname}from"next/navigation";
const links=[["Mensual","/reports/monthly"],["Clientes","/reports/clients"],["Vehículos","/reports/vehicles"],["Cuentas por cobrar","/reports/receivables"]];
export default function ReportNav(){const path=usePathname();return <nav className="mb-6 flex gap-2 overflow-x-auto pb-1">{links.map(([label,href])=><Link key={href} href={href} className={`shrink-0 rounded-xl px-4 py-2 text-sm font-bold ${path===href?"bg-slate-900 text-white":"border border-slate-200 bg-white text-slate-600"}`}>{label}</Link>)}</nav>}

