"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { ApiError, api } from "@/lib/api";
import { ErrorMessage } from "@/components/ui";

export default function LoginPage() {
  const router = useRouter(); const [error, setError] = useState(""); const [pending, setPending] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setPending(true); setError("");
    const form = new FormData(event.currentTarget);
    try { await api("/auth/login", { method: "POST", body: JSON.stringify({ username: form.get("username"), password: form.get("password") }) }); router.replace("/dashboard"); }
    catch (err) { setError(err instanceof ApiError ? err.message : "No fue posible iniciar sesión."); setPending(false); }
  }
  return <main className="relative grid min-h-screen place-items-center overflow-hidden bg-slate-950 p-5">
    <div className="absolute -left-24 top-12 h-72 w-72 rounded-full bg-emerald-500/20 blur-3xl" /><div className="absolute -bottom-20 right-0 h-80 w-80 rounded-full bg-sky-400/10 blur-3xl" />
    <section className="relative w-full max-w-md rounded-3xl border border-white/10 bg-white p-7 shadow-2xl sm:p-9">
      <p className="text-xs font-bold uppercase tracking-[.24em] text-emerald-700">Transker</p><h1 className="mt-2 text-3xl font-bold text-slate-950">Bienvenido</h1><p className="mt-2 text-sm text-slate-500">Ingresa para gestionar la operación.</p>
      <form className="mt-8 space-y-5" onSubmit={submit}>{error && <ErrorMessage message={error} />}<div className="field"><label htmlFor="username">Usuario</label><input id="username" name="username" autoComplete="username" required autoFocus /></div><div className="field"><label htmlFor="password">Contraseña</label><input id="password" name="password" type="password" autoComplete="current-password" minLength={8} required /></div><button disabled={pending} className="btn-primary w-full" type="submit">{pending ? "Ingresando…" : "Ingresar"}</button></form>
      <p className="mt-6 text-center text-xs text-slate-400">Acceso exclusivo para personal autorizado</p>
    </section>
  </main>;
}

