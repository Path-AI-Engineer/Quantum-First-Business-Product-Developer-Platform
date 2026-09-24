import type { NextRequest } from "next/server";
const allowed = new Set(["room", "score", "economics", "thesis", "handoff"]);
const backend = process.env.VENTURE_API_BASE ?? "http://127.0.0.1:8955";
export async function GET(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  const { path } = await context.params;
  if (path.length !== 1 || !allowed.has(path[0]))
    return Response.json({ detail: "Not found" }, { status: 404 });
  try {
    const response = await fetch(
      `${backend}/api/${path[0]}${request.nextUrl.search}`,
      { cache: "no-store", signal: AbortSignal.timeout(15000) },
    );
    const headers = new Headers({
      "Content-Type":
        response.headers.get("content-type") ?? "application/json",
      "Cache-Control": "no-store",
    });
    const disposition = response.headers.get("content-disposition");
    if (disposition) headers.set("Content-Disposition", disposition);
    return new Response(response.body, { status: response.status, headers });
  } catch {
    return Response.json(
      {
        detail:
          "Evidence API unavailable. Check the configured API endpoint and retry.",
      },
      { status: 503 },
    );
  }
}
