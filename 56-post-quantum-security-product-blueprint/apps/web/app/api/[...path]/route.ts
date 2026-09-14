import { NextRequest, NextResponse } from "next/server";

const backend = process.env.PQC_API_BASE ?? "http://127.0.0.1:8056";

async function relay(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  if (!path?.length || path[0] !== "v1" || path.some((part) => part === "..")) {
    return NextResponse.json({ detail: "Unsupported local API path" }, { status: 404 });
  }
  const url = `${backend}/${path.map(encodeURIComponent).join("/")}${request.nextUrl.search}`;
  const identity = request.headers.get("x-demo-identity") ?? "";
  const upstream = await fetch(url, {
    method: request.method,
    headers: { "content-type": "application/json", "x-demo-identity": identity },
    body: request.method === "GET" ? undefined : await request.text(),
    cache: "no-store",
  });
  const body = await upstream.text();
  return new NextResponse(body, {
    status: upstream.status,
    headers: { "content-type": upstream.headers.get("content-type") ?? "application/json", "cache-control": "no-store" },
  });
}

export const GET = relay;
export const POST = relay;
