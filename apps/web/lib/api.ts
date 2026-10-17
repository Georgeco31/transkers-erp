export class ApiError extends Error {
  constructor(public status: number, message: string) { super(message); }
}

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`/api/v1${path}`, {
    ...options,
    credentials: "include",
    headers: { "Content-Type": "application/json", ...(options.headers ?? {}) },
  });
  if (!response.ok) {
    let detail = "No fue posible completar la operación.";
    try {
      const body = await response.json();
      detail = typeof body.detail === "string" ? body.detail : detail;
    } catch { /* response had no JSON body */ }
    throw new ApiError(response.status, detail);
  }
  return response.json() as Promise<T>;
}

export const money = (value: string | number | null | undefined) =>
  new Intl.NumberFormat("es-EC", { style: "currency", currency: "USD" }).format(Number(value ?? 0));

export const shortDate = (value: string | null | undefined) =>
  value ? new Intl.DateTimeFormat("es-EC", { timeZone: "UTC" }).format(new Date(`${value.slice(0, 10)}T00:00:00Z`)) : "—";

export const today = () => new Date().toISOString().slice(0, 10);

