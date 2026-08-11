import Link from "next/link";
import type { ReactNode } from "react";

export function PageHeader({ eyebrow, title, description, action }: { eyebrow?: string; title: string; description?: string; action?: ReactNode }) {
  return <header className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
    <div>{eyebrow && <p className="mb-1 text-xs font-bold uppercase tracking-[.18em] text-emerald-700">{eyebrow}</p>}<h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">{title}</h1>{description && <p className="mt-2 max-w-2xl text-sm text-slate-500">{description}</p>}</div>
    {action}
  </header>;
}

export function Metric({ label, value, hint, tone = "default" }: { label: string; value: ReactNode; hint?: string; tone?: "default" | "positive" | "negative" }) {
  const color = tone === "positive" ? "text-emerald-700" : tone === "negative" ? "text-rose-700" : "text-slate-900";
  return <article className="panel"><p className="text-xs font-bold uppercase tracking-wide text-slate-500">{label}</p><p className={`mt-2 text-2xl font-bold ${color}`}>{value}</p>{hint && <p className="mt-1 text-xs text-slate-500">{hint}</p>}</article>;
}

export function Empty({ children = "No hay registros para mostrar." }: { children?: ReactNode }) {
  return <div className="panel py-12 text-center text-sm text-slate-500">{children}</div>;
}

export function ErrorMessage({ message }: { message: string }) {
  return <div role="alert" className="mb-4 rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm font-medium text-rose-700">{message}</div>;
}

export function StatusBadge({ status }: { status: string }) {
  const map: Record<string, [string, string]> = { completed: ["Completado", "bg-emerald-50 text-emerald-700"], draft: ["Borrador", "bg-amber-50 text-amber-700"], cancelled: ["Cancelado", "bg-rose-50 text-rose-700"], maintenance: ["Mantenimiento", "bg-sky-50 text-sky-700"], repair: ["Reparación", "bg-orange-50 text-orange-700"] };
  const [label, cls] = map[status] ?? [status, "bg-slate-100 text-slate-700"];
  return <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-bold ${cls}`}>{label}</span>;
}

export function BackLink({ href, children = "Volver" }: { href: string; children?: ReactNode }) {
  return <Link href={href} className="mb-4 inline-flex text-sm font-semibold text-emerald-700 hover:text-emerald-900">← {children}</Link>;
}

export function SubmitButton({ pending, children }: { pending: boolean; children: ReactNode }) {
  return <button type="submit" disabled={pending} className="btn-primary">{pending ? "Guardando…" : children}</button>;
}

