"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, money, shortDate } from "@/lib/api";
import { useQueryFlag } from "@/lib/use-query-flag";
import { Empty, PageHeader, StatusBadge, SuccessMessage } from "@/components/ui";

type Item = {
  id: number;
  expense_date: string;
  vehicle_plate: string;
  expense_type: string;
  description: string;
  amount: string;
  odometer?: number | null;
};

export default function Page() {
  const [items, setItems] = useState<Item[]>([]);
  const [type, setType] = useState("");
  const updated = useQueryFlag("expense_updated");

  useEffect(() => {
    api<Item[]>(`/vehicle-expenses${type ? `?expense_type=${type}` : ""}`).then(setItems);
  }, [type]);

  return (
    <>
      <PageHeader
        eyebrow="Flota"
        title="Gastos de vehículos"
        description="Mantenimientos y reparaciones registrados por vehículo."
        action={<Link href="/vehicle-expenses/new" className="btn-primary">+ Registrar gasto</Link>}
      />
      {updated && <SuccessMessage message="El gasto vehicular se actualizó correctamente." />}
      <div className="panel mb-5 sm:max-w-xs">
        <label htmlFor="type">Tipo</label>
        <select id="type" className="mt-2" value={type} onChange={(event) => setType(event.target.value)}>
          <option value="">Todos</option>
          <option value="maintenance">Mantenimiento</option>
          <option value="repair">Reparación</option>
        </select>
      </div>
      {items.length ? (
        <div className="panel overflow-hidden p-0">
          <table className="data-table responsive-table">
            <thead><tr><th>Fecha</th><th>Vehículo</th><th>Tipo</th><th>Descripción</th><th>Kilometraje</th><th>Monto</th><th>Acciones</th></tr></thead>
            <tbody>{items.map((item) => (
              <tr key={item.id}>
                <td data-label="Fecha">{shortDate(item.expense_date)}</td>
                <td data-label="Vehículo" className="font-bold">{item.vehicle_plate}</td>
                <td data-label="Tipo"><StatusBadge status={item.expense_type} /></td>
                <td data-label="Descripción">{item.description}</td>
                <td data-label="Kilometraje">{item.odometer?.toLocaleString("es-EC") ?? "—"}</td>
                <td data-label="Monto" className="font-bold">{money(item.amount)}</td>
                <td data-label="Acciones"><Link className="btn-secondary" href={`/vehicle-expenses/${item.id}/edit`}>Editar</Link></td>
              </tr>
            ))}</tbody>
          </table>
        </div>
      ) : <Empty>No hay gastos vehiculares registrados.</Empty>}
    </>
  );
}
