"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, money, shortDate } from "@/lib/api";
import { useQueryFlag } from "@/lib/use-query-flag";
import { BackLink, Metric, PageHeader, StatusBadge, SuccessMessage } from "@/components/ui";

type Kind = "clients" | "drivers" | "vehicles";
type Trip = {
  id: number;
  code: string;
  trip_date: string;
  client_name: string;
  vehicle_plate: string;
  driver_name: string;
  agreed_price: string;
  margin: string;
  status: string;
};
type Detail = {
  id: number;
  name?: string;
  plate?: string;
  brand?: string;
  model?: string;
  year?: number;
  phone?: string;
  tax_id?: string;
  notes?: string;
  is_active: boolean;
  trip_count?: number;
  billed?: string;
  paid?: string;
  pending?: string;
  credit?: string;
  income?: string;
  direct_expenses?: string;
  maintenance?: string;
  repairs?: string;
  operating_result?: string;
  trips: Trip[];
  payments?: { id: number; payment_date: string; amount: string; allocated: string; reference?: string }[];
  expenses?: { id: number; expense_type: string; expense_date: string; amount: string; description: string }[];
};

export default function CatalogDetail({ kind, id }: { kind: Kind; id: string }) {
  const [data, setData] = useState<Detail | null>(null);
  const paymentUpdated = useQueryFlag("payment_updated");
  const expenseUpdated = useQueryFlag("expense_updated");

  useEffect(() => {
    api<Detail>(`/${kind}/${id}`).then(setData);
  }, [kind, id]);

  if (!data) return <p className="text-sm text-slate-500">Cargando ficha…</p>;
  const title = data.name ?? data.plate ?? "Ficha";

  return (
    <>
      <BackLink href={`/${kind}`} />
      <PageHeader
        eyebrow="Ficha"
        title={title}
        description={kind === "vehicles"
          ? [data.brand, data.model, data.year].filter(Boolean).join(" · ") || "Datos del vehículo"
          : data.is_active ? "Registro activo" : "Registro inactivo"}
        action={<Link className="btn-secondary" href={`/${kind}/${id}/edit`}>Editar</Link>}
      />
      {paymentUpdated && <SuccessMessage message="El pago se actualizó y los saldos del cliente se recalcularon." />}
      {expenseUpdated && <SuccessMessage message="El gasto vehicular se actualizó correctamente." />}

      {kind === "clients" && (
        <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <Metric label="Viajes" value={data.trip_count ?? 0} />
          <Metric label="Facturado" value={money(data.billed)} />
          <Metric label="Pagado" value={money(data.paid)} tone="positive" />
          <Metric label="Pendiente" value={money(data.pending)} tone="negative" />
          <Metric label="Saldo a favor" value={money(data.credit)} />
        </section>
      )}
      {kind === "vehicles" && (
        <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <Metric label="Viajes" value={data.trip_count ?? 0} />
          <Metric label="Ingresos" value={money(data.income)} />
          <Metric label="Gastos directos" value={money(data.direct_expenses)} />
          <Metric label="Mantenimiento" value={money(data.maintenance)} />
          <Metric label="Reparaciones" value={money(data.repairs)} />
          <Metric label="Resultado operativo" value={money(data.operating_result)} tone={Number(data.operating_result) >= 0 ? "positive" : "negative"} />
        </section>
      )}
      {kind === "clients" && (
        <div className="panel mt-5">
          <h2 className="font-bold">Datos generales</h2>
          <dl className="mt-3 grid gap-3 text-sm sm:grid-cols-3">
            <div><dt className="text-slate-500">RUC / identificación</dt><dd className="font-semibold">{data.tax_id || "—"}</dd></div>
            <div><dt className="text-slate-500">Teléfono</dt><dd className="font-semibold">{data.phone || "—"}</dd></div>
            <div><dt className="text-slate-500">Notas</dt><dd className="font-semibold">{data.notes || "—"}</dd></div>
          </dl>
        </div>
      )}

      <div className="panel mt-6 overflow-hidden p-0">
        <div className="p-5"><h2 className="font-bold">Historial de viajes</h2></div>
        <table className="data-table responsive-table">
          <thead><tr><th>Fecha</th><th>Código</th>{kind !== "clients" && <th>Cliente</th>}{kind !== "vehicles" && <th>Vehículo</th>}{kind !== "drivers" && <th>Chofer</th>}<th>Precio</th><th>Estado</th></tr></thead>
          <tbody>{data.trips?.map((trip) => (
            <tr key={trip.id}>
              <td data-label="Fecha">{shortDate(trip.trip_date)}</td>
              <td data-label="Código"><Link href={`/trips/${trip.id}`} className="font-bold text-emerald-700">{trip.code}</Link></td>
              {kind !== "clients" && <td data-label="Cliente">{trip.client_name}</td>}
              {kind !== "vehicles" && <td data-label="Vehículo">{trip.vehicle_plate}</td>}
              {kind !== "drivers" && <td data-label="Chofer">{trip.driver_name}</td>}
              <td data-label="Precio">{money(trip.agreed_price)}</td>
              <td data-label="Estado"><StatusBadge status={trip.status} /></td>
            </tr>
          ))}</tbody>
        </table>
        {!data.trips?.length && <p className="p-5 text-sm text-slate-500">Sin viajes registrados.</p>}
      </div>

      {kind === "clients" && (
        <div className="panel mt-6 overflow-hidden p-0">
          <div className="flex flex-wrap items-center justify-between gap-3 p-5">
            <h2 className="font-bold">Historial de pagos</h2>
            <Link className="font-bold text-emerald-700" href={`/payments/new?client_id=${id}`}>Registrar pago</Link>
          </div>
          <table className="data-table responsive-table">
            <thead><tr><th>Fecha</th><th>Monto</th><th>Aplicado</th><th>Referencia</th><th>Acciones</th></tr></thead>
            <tbody>{data.payments?.map((payment) => (
              <tr key={payment.id}>
                <td data-label="Fecha">{shortDate(payment.payment_date)}</td>
                <td data-label="Monto">{money(payment.amount)}</td>
                <td data-label="Aplicado">{money(payment.allocated)}</td>
                <td data-label="Referencia">{payment.reference || "—"}</td>
                <td data-label="Acciones">
                  <Link className="btn-secondary" href={`/payments/${payment.id}/edit?return_to=/clients/${id}`}>Editar</Link>
                </td>
              </tr>
            ))}</tbody>
          </table>
          {!data.payments?.length && <p className="p-5 text-sm text-slate-500">Sin pagos registrados.</p>}
        </div>
      )}

      {kind === "vehicles" && (
        <div className="panel mt-6 overflow-hidden p-0">
          <div className="flex flex-wrap items-center justify-between gap-3 p-5">
            <h2 className="font-bold">Mantenimientos y reparaciones</h2>
            <Link className="font-bold text-emerald-700" href={`/vehicle-expenses/new?vehicle_id=${id}`}>Registrar gasto</Link>
          </div>
          <table className="data-table responsive-table">
            <thead><tr><th>Fecha</th><th>Tipo</th><th>Descripción</th><th>Monto</th><th>Acciones</th></tr></thead>
            <tbody>{data.expenses?.map((expense) => (
              <tr key={expense.id}>
                <td data-label="Fecha">{shortDate(expense.expense_date)}</td>
                <td data-label="Tipo"><StatusBadge status={expense.expense_type} /></td>
                <td data-label="Descripción">{expense.description}</td>
                <td data-label="Monto">{money(expense.amount)}</td>
                <td data-label="Acciones">
                  <Link className="btn-secondary" href={`/vehicle-expenses/${expense.id}/edit?return_to=/vehicles/${id}`}>Editar</Link>
                </td>
              </tr>
            ))}</tbody>
          </table>
          {!data.expenses?.length && <p className="p-5 text-sm text-slate-500">Sin gastos registrados.</p>}
        </div>
      )}
    </>
  );
}
