import { NextRequest, NextResponse } from "next/server";

const backend = process.env.API_BASE_URL || "http://127.0.0.1:8058";

async function proxy(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  const target = new URL(`/v1/${path.join("/")}`, backend);
  request.nextUrl.searchParams.forEach((value, key) => target.searchParams.set(key, value));
  const headers = new Headers(request.headers);
  headers.delete("host");
  const response = await fetch(target, {
    method: request.method,
    headers,
    body: ["GET", "HEAD"].includes(request.method) ? undefined : await request.text(),
    cache: "no-store",
  });
  return new NextResponse(response.body, { status: response.status, headers: response.headers });
}

export const GET = proxy;
export const POST = proxy;
export const DELETE = proxy;

