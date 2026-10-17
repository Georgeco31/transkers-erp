"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, money, shortDate } from "@/lib/api";
import { useQueryFlag } from "@/lib/use-query-flag";
import { Empty, PageHeader, SuccessMessage } from "@/components/ui";

type Payment = {
  id: number;
  payment_date: string;
  client_name: string;
  amount: string;
  allocated: string;
  unapplied: string;
  payment_method?: string;
  reference?: string;
};

export default function Page() {
  const [items, setItems] = useState<Payment[]>([]);
  const updated = useQueryFlag("payment_updated");

  useEffect(() => {
    api<Payment[]>("/payments").then(setItems);
  }, []);

  return (
    <>
      <PageHeader
        eyebrow="Cobranzas"
        title="Pagos de clientes"
        description="Los pagos se aplican automáticamente a los viajes completados más antiguos."
        action={<Link className="btn-primary" href="/payments/new">+ Registrar pago</Link>}
      />
      {updated && <SuccessMessage message="El pago se actualizó y sus asignaciones se recalcularon correctamente." />}
      {items.length ? (
        <div className="panel overflow-hidden p-0">
          <table className="data-table responsive-table">
            <thead><tr><th>Fecha</th><th>Cliente</th><th>Monto</th><th>Aplicado</th><th>Saldo a favor</th><th>Método</th><th>Referencia</th><th>Acciones</th></tr></thead>
            <tbody>{items.map((item) => (
              <tr key={item.id}>
                <td data-label="Fecha">{shortDate(item.payment_date)}</td>
                <td data-label="Cliente" className="font-semibold">{item.client_name}</td>
                <td data-label="Monto" className="font-bold">{money(item.amount)}</td>
                <td data-label="Aplicado">{money(item.allocated)}</td>
                <td data-label="Saldo a favor">{money(item.unapplied)}</td>
                <td data-label="Método">{item.payment_method || "—"}</td>
                <td data-label="Referencia">{item.reference || "—"}</td>
                <td data-label="Acciones"><Link className="btn-secondary" href={`/payments/${item.id}/edit`}>Editar</Link></td>
              </tr>
            ))}</tbody>
          </table>
        </div>
      ) : <Empty>No hay pagos registrados.</Empty>}
    </>
  );
}
