// Fetch-style handler: works on Cloudflare Workers, Vercel/Netlify edge, Deno, Node 20+.
// Secrets/config come from env — nothing is stored in the repo:
//   ALLOWED_ORIGINS  comma list, e.g. https://inonda.example
//   LEAD_WEBHOOK_URL where enriched leads are POSTed (Zapier / Make / Composio / Slack-compatible)
import { validate, isSpam, enrich } from "./lead.js";
import { buildReply } from "./replies.js";

const json = (obj, status, origin) =>
  new Response(JSON.stringify(obj), {
    status,
    headers: { "content-type": "application/json", ...(origin ? { "access-control-allow-origin": origin, vary: "origin" } : {}) },
  });

export async function handle(request, env, { now = new Date(), fetchImpl = fetch } = {}) {
  const allowed = String(env.ALLOWED_ORIGINS || "").split(",").map((s) => s.trim()).filter(Boolean);
  const origin = request.headers.get("origin") || "";
  const okOrigin = allowed.includes(origin) ? origin : "";

  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: okOrigin ? { "access-control-allow-origin": okOrigin, "access-control-allow-methods": "POST", "access-control-allow-headers": "content-type", vary: "origin" } : {} });
  }
  if (request.method !== "POST") return json({ error: "method_not_allowed" }, 405, okOrigin);
  if (allowed.length && !okOrigin) return json({ error: "forbidden_origin" }, 403);

  let body;
  try {
    const text = await request.text();
    if (text.length > 20000) return json({ error: "too_large" }, 413, okOrigin);
    body = JSON.parse(text);
  } catch { return json({ error: "bad_json" }, 400, okOrigin); }

  // Bots get a fake success so they don't adapt.
  if (isSpam(body)) return json({ ok: true }, 200, okOrigin);

  const { ok, errors, lead } = validate(body);
  if (!ok) return json({ error: "invalid", fields: errors }, 422, okOrigin);

  const enriched = enrich(lead, { pageLang: body.lang, page: body.page, now });
  const payload = { lead: enriched, auto_reply: buildReply(enriched) };

  if (!env.LEAD_WEBHOOK_URL) return json({ error: "not_configured" }, 503, okOrigin);
  const res = await fetchImpl(env.LEAD_WEBHOOK_URL, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(payload) });
  if (!res.ok) return json({ error: "delivery_failed" }, 502, okOrigin);
  return json({ ok: true }, 200, okOrigin);
}

export default { fetch: (req, env) => handle(req, env) };
