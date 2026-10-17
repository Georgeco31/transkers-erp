"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, money, shortDate } from "@/lib/api";
import { Empty, Metric, PageHeader, StatusBadge } from "@/components/ui";

type Trip = { id: number; trip_date: string; client_name: string; vehicle_plate: string; driver_name: string; agreed_price: string; status: string };
type Dashboard = { trip_count: number; income: string; collected: string; accounts_receivable: string; trip_expenses: string; maintenance: string; repairs: string; operating_result: string; recent_trips: Trip[]; top_debtors: { id:number; name:string; pending:string }[] };

export default function DashboardPage() {
  const now = new Date(); const [period, setPeriod] = useState(`${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,"0")}`); const [data, setData] = useState<Dashboard | null>(null);
  useEffect(() => { const [year, month] = period.split("-"); api<Dashboard>(`/reports/dashboard?year=${year}&month=${month}`).then(setData); }, [period]);
  return <><PageHeader eyebrow="Resumen mensual" title="Inicio" description="Una lectura clara de la operación registrada." action={<div className="w-full sm:w-44"><label className="sr-only" htmlFor="period">Mes</label><input id="period" type="month" value={period} onChange={e=>setPeriod(e.target.value)} /></div>} />
    <div className="mb-6 grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4"><Link className="btn-primary" href="/trips/new">+ Nuevo viaje</Link><Link className="btn-secondary" href="/payments/new">+ Registrar pago</Link><Link className="btn-secondary" href="/vehicle-expenses/new">+ Gasto vehicular</Link><Link className="btn-secondary" href="/reports/monthly">Ver reportes</Link></div>
    {!data ? <p className="text-sm text-slate-500">Cargando indicadores…</p> : <><section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"><Metric label="Viajes realizados" value={data.trip_count} /><Metric label="Ingresos" value={money(data.income)} /><Metric label="Cobrado" value={money(data.collected)} /><Metric label="Cuentas por cobrar" value={money(data.accounts_receivable)} tone="negative" /><Metric label="Gastos de viajes" value={money(data.trip_expenses)} /><Metric label="Mantenimiento" value={money(data.maintenance)} /><Metric label="Reparaciones" value={money(data.repairs)} /><Metric label="Utilidad operativa registrada" value={money(data.operating_result)} tone={Number(data.operating_result) >= 0 ? "positive" : "negative"} hint="No equivale a utilidad neta contable." /></section>
      <section className="mt-6 grid gap-6 xl:grid-cols-[2fr_1fr]"><div className="panel overflow-hidden p-0"><div className="p-5"><h2 className="font-bold text-slate-900">Últimos viajes</h2></div>{data.recent_trips.length ? <table className="data-table responsive-table"><thead><tr><th>Fecha</th><th>Cliente</th><th>Vehículo</th><th>Chofer</th><th>Precio</th><th>Estado</th></tr></thead><tbody>{data.recent_trips.map(x=><tr key={x.id}><td data-label="Fecha">{shortDate(x.trip_date)}</td><td data-label="Cliente"><Link className="font-semibold text-emerald-700" href={`/trips/${x.id}`}>{x.client_name}</Link></td><td data-label="Vehículo">{x.vehicle_plate}</td><td data-label="Chofer">{x.driver_name}</td><td data-label="Precio">{money(x.agreed_price)}</td><td data-label="Estado"><StatusBadge status={x.status}/></td></tr>)}</tbody></table> : <div className="p-5"><Empty /></div>}</div>
      <div className="panel"><h2 className="font-bold text-slate-900">Clientes con mayor saldo</h2><div className="mt-4 space-y-3">{data.top_debtors.length ? data.top_debtors.map(x=><Link key={x.id} href={`/clients/${x.id}`} className="flex min-h-12 items-center justify-between rounded-xl bg-slate-50 px-3 py-2 hover:bg-slate-100"><span className="text-sm font-semibold">{x.name}</span><span className="font-bold text-rose-700">{money(x.pending)}</span></Link>) : <p className="text-sm text-slate-500">No hay saldos pendientes.</p>}</div></div></section></>}
  </>;
}

