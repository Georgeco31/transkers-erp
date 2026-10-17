"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ApiError, api, today } from "@/lib/api";
import { BackLink, ErrorMessage, PageHeader, SubmitButton } from "@/components/ui";

type Vehicle = { id: number; plate: string };
type VehicleExpense = {
  id: number;
  vehicle_id: number;
  vehicle_plate: string;
  expense_type: "maintenance" | "repair";
  expense_date: string;
  amount: string;
  description: string;
  odometer: number | null;
};

export default function VehicleExpenseForm({
  id,
  defaultVehicleId = "",
  returnTo = "/vehicle-expenses",
}: {
  id?: string;
  defaultVehicleId?: string;
  returnTo?: string;
}) {
  const router = useRouter();
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [initial, setInitial] = useState<VehicleExpense | null>(
    id
      ? null
      : {
          id: 0,
          vehicle_id: Number(defaultVehicleId || 0),
          vehicle_plate: "",
          expense_type: "maintenance",
          expense_date: today(),
          amount: "",
          description: "",
          odometer: null,
        },
  );
  const [selectedVehicle, setSelectedVehicle] = useState(defaultVehicleId);
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);

  useEffect(() => {
    if (id) {
      api<VehicleExpense>(`/vehicle-expenses/${id}`)
        .then((expense) => {
          setInitial(expense);
          setSelectedVehicle(String(expense.vehicle_id));
        })
        .catch((err) => setError(err instanceof ApiError ? err.message : "No se pudo cargar el gasto."));
      return;
    }
    api<Vehicle[]>("/vehicles?active=true")
      .then(setVehicles)
      .catch((err) => setError(err instanceof ApiError ? err.message : "No se pudieron cargar los vehículos."));
  }, [id]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!initial) return;
    setPending(true);
    setError("");
    const form = new FormData(event.currentTarget);
    const payload = {
      vehicle_id: id ? initial.vehicle_id : Number(form.get("vehicle_id")),
      expense_type: form.get("expense_type"),
      expense_date: form.get("expense_date"),
      amount: form.get("amount"),
      description: form.get("description"),
      odometer: form.get("odometer") ? Number(form.get("odometer")) : null,
    };
    try {
      await api(`/vehicle-expenses${id ? `/${id}` : ""}`, {
        method: id ? "PUT" : "POST",
        body: JSON.stringify(payload),
      });
      const separator = returnTo.includes("?") ? "&" : "?";
      router.push(id ? `${returnTo}${separator}expense_updated=1` : returnTo);
      router.refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo guardar el gasto.");
      setPending(false);
    }
  }

  if (!initial) {
    return error ? <ErrorMessage message={error} /> : <p className="text-sm text-slate-500">Cargando gasto…</p>;
  }

  return (
    <>
      <BackLink href={returnTo} />
      <PageHeader
        eyebrow="Flota"
        title={id ? "Editar gasto vehicular" : "Registrar gasto vehicular"}
        description="La fecha del gasto determina el período de los reportes financieros."
      />
      <form onSubmit={submit} className="panel max-w-2xl space-y-5">
        {error && <ErrorMessage message={error} />}
        <div className="field">
          <label htmlFor={id ? "vehicle_name" : "vehicle_id"}>Vehículo *</label>
          {id ? (
            <input id="vehicle_name" value={initial.vehicle_plate} disabled />
          ) : (
            <select
              id="vehicle_id"
              name="vehicle_id"
              required
              value={selectedVehicle}
              onChange={(event) => setSelectedVehicle(event.target.value)}
            >
              <option value="">Seleccionar</option>
              {vehicles.map((vehicle) => (
                <option key={vehicle.id} value={vehicle.id}>{vehicle.plate}</option>
              ))}
            </select>
          )}
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="field">
            <label htmlFor="expense_type">Tipo *</label>
            <select id="expense_type" name="expense_type" required defaultValue={initial.expense_type}>
              <option value="maintenance">Mantenimiento</option>
              <option value="repair">Reparación</option>
            </select>
          </div>
          <div className="field">
            <label htmlFor="expense_date">Fecha del gasto *</label>
            <input id="expense_date" name="expense_date" type="date" defaultValue={initial.expense_date} required />
          </div>
          <div className="field">
            <label htmlFor="amount">Monto USD *</label>
            <input id="amount" name="amount" type="number" step="0.01" min="0.01" inputMode="decimal" defaultValue={initial.amount} required />
          </div>
          <div className="field">
            <label htmlFor="odometer">Kilometraje (opcional)</label>
            <input id="odometer" name="odometer" type="number" min="0" inputMode="numeric" defaultValue={initial.odometer ?? ""} />
          </div>
        </div>
        <div className="field">
          <label htmlFor="description">Descripción *</label>
          <textarea id="description" name="description" rows={3} defaultValue={initial.description} required />
        </div>
        <div className="flex flex-wrap gap-3">
          <SubmitButton pending={pending}>{id ? "Guardar cambios" : "Registrar gasto"}</SubmitButton>
          <Link href={returnTo} className="btn-secondary">Cancelar</Link>
        </div>
      </form>
    </>
  );
}
