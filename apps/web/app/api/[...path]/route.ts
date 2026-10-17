import type { NextRequest } from "next/server";

type Context = { params: Promise<{ path: string[] }> };

async function proxy(request: NextRequest, context: Context): Promise<Response> {
  const { path } = await context.params;
  const base = process.env.API_INTERNAL_URL ?? "http://localhost:8000";
  const upstream = new URL(`/api/${path.join("/")}`, base);
  upstream.search = request.nextUrl.search;
  const headers = new Headers(request.headers);
  headers.delete("host");
  headers.delete("content-length");
  headers.delete("connection");
  headers.delete("expect");
  const hasBody = request.method !== "GET" && request.method !== "HEAD";
  const response = await fetch(upstream, {
    method: request.method,
    headers,
    body: hasBody ? await request.arrayBuffer() : undefined,
    redirect: "manual",
    cache: "no-store",
  });
  return new Response(response.body, { status: response.status, headers: response.headers });
}

export const dynamic = "force-dynamic";
export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
export const OPTIONS = proxy;
