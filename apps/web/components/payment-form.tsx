"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ApiError, api, today } from "@/lib/api";
import { BackLink, ErrorMessage, PageHeader, SubmitButton } from "@/components/ui";

type Client = { id: number; name: string; pending: string; credit: string };
type Payment = {
  id: number;
  client_id: number;
  client_name: string;
  payment_date: string;
  amount: string;
  payment_method: string | null;
  reference: string | null;
  notes: string | null;
};
const PAYMENT_METHODS = ["Transferencia", "Efectivo", "Cheque", "Depósito"];

export default function PaymentForm({
  id,
  defaultClientId = "",
  returnTo = "/payments",
}: {
  id?: string;
  defaultClientId?: string;
  returnTo?: string;
}) {
  const router = useRouter();
  const [clients, setClients] = useState<Client[]>([]);
  const [initial, setInitial] = useState<Payment | null>(
    id
      ? null
      : {
          id: 0,
          client_id: Number(defaultClientId || 0),
          client_name: "",
          payment_date: today(),
          amount: "",
          payment_method: null,
          reference: null,
          notes: null,
        },
  );
  const [selectedClient, setSelectedClient] = useState(defaultClientId);
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);

  useEffect(() => {
    if (id) {
      api<Payment>(`/payments/${id}`)
        .then((payment) => {
          setInitial(payment);
          setSelectedClient(String(payment.client_id));
        })
        .catch((err) => setError(err instanceof ApiError ? err.message : "No se pudo cargar el pago."));
      return;
    }
    api<Client[]>("/clients?active=true")
      .then(setClients)
      .catch((err) => setError(err instanceof ApiError ? err.message : "No se pudieron cargar los clientes."));
  }, [id]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    setError("");
    const form = new FormData(event.currentTarget);
    const editable = {
      payment_date: form.get("payment_date"),
      amount: form.get("amount"),
      payment_method: form.get("payment_method") || null,
      reference: form.get("reference") || null,
      notes: form.get("notes") || null,
    };
    const payload = id
      ? editable
      : { ...editable, client_id: Number(form.get("client_id")), auto_allocate: true };
    try {
      await api(`/payments${id ? `/${id}` : ""}`, {
        method: id ? "PUT" : "POST",
        body: JSON.stringify(payload),
      });
      const separator = returnTo.includes("?") ? "&" : "?";
      router.push(id ? `${returnTo}${separator}payment_updated=1` : returnTo);
      router.refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo guardar el pago.");
      setPending(false);
    }
  }

  if (!initial) {
    return error ? <ErrorMessage message={error} /> : <p className="text-sm text-slate-500">Cargando pago…</p>;
  }

  return (
    <>
      <BackLink href={returnTo} />
      <PageHeader
        eyebrow="Cobranzas"
        title={id ? "Editar pago" : "Registrar pago"}
        description={id
          ? "Si cambia el monto, las asignaciones se recalcularán desde los viajes pendientes más antiguos."
          : "El sistema lo asignará a los viajes pendientes más antiguos del cliente. Cualquier excedente quedará como saldo a favor."}
      />
      <form onSubmit={submit} className="panel max-w-2xl space-y-5">
        {error && <ErrorMessage message={error} />}
        <div className="field">
          <label htmlFor={id ? "client_name" : "client_id"}>Cliente *</label>
          {id ? (
            <input id="client_name" value={initial.client_name} disabled />
          ) : (
            <select
              id="client_id"
              name="client_id"
              required
              value={selectedClient}
              onChange={(event) => setSelectedClient(event.target.value)}
            >
              <option value="">Seleccionar</option>
              {clients.map((client) => (
                <option key={client.id} value={client.id}>{client.name} · pendiente ${client.pending}</option>
              ))}
            </select>
          )}
          {id && <p className="text-xs text-slate-500">El cliente no puede cambiarse desde esta operación.</p>}
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="field">
            <label htmlFor="payment_date">Fecha del pago *</label>
            <input id="payment_date" name="payment_date" type="date" defaultValue={initial.payment_date} required />
          </div>
          <div className="field">
            <label htmlFor="amount">Monto USD *</label>
            <input id="amount" name="amount" type="number" step="0.01" min="0.01" inputMode="decimal" defaultValue={initial.amount} required />
          </div>
          <div className="field">
            <label htmlFor="payment_method">Forma de pago</label>
            <select id="payment_method" name="payment_method" defaultValue={initial.payment_method ?? ""}>
              <option value="">No indicado</option>
              {initial.payment_method && !PAYMENT_METHODS.includes(initial.payment_method) && (
                <option value={initial.payment_method}>{initial.payment_method}</option>
              )}
              {PAYMENT_METHODS.map((method) => <option key={method}>{method}</option>)}
            </select>
          </div>
          <div className="field">
            <label htmlFor="reference">Referencia</label>
            <input id="reference" name="reference" defaultValue={initial.reference ?? ""} />
          </div>
        </div>
        <div className="field">
          <label htmlFor="notes">Observaciones</label>
          <textarea id="notes" name="notes" rows={3} defaultValue={initial.notes ?? ""} />
        </div>
        <div className="flex flex-wrap gap-3">
          <SubmitButton pending={pending}>{id ? "Guardar cambios" : "Registrar pago"}</SubmitButton>
          <Link href={returnTo} className="btn-secondary">Cancelar</Link>
        </div>
      </form>
    </>
  );
}
