import test from "node:test";
import assert from "node:assert/strict";
import { validate, isSpam, enrich, detectLanguage, classify } from "../src/lead.js";
import { handle } from "../src/handler.js";
import { buildReply } from "../src/replies.js";

const good = { name: "Anna", email: "Anna@Example.com", phone: "+357 99 123456", subject: "Manage my apartment", message: "I am an owner in Nicosia." };
const req = (body, headers = {}, method = "POST") => new Request("https://x.test/", { method, headers: { origin: "https://inonda.test", ...headers }, body: method === "POST" ? JSON.stringify(body) : undefined });
const env = { ALLOWED_ORIGINS: "https://inonda.test", LEAD_WEBHOOK_URL: "https://hook.test/x" };

test("validate accepts good lead, normalises email", () => {
  const r = validate(good); assert.ok(r.ok); assert.equal(r.lead.email, "anna@example.com");
});
test("validate rejects bad email, header injection", () => {
  assert.deepEqual(validate({ ...good, email: "nope" }).errors, ["email"]);
  assert.ok(validate({ ...good, subject: "hi\r\nBcc: x@y.z" }).errors.includes("newline"));
});
test("spam: honeypot and link stuffing", () => {
  assert.ok(isSpam({ ...good, _kleap_hp: "bot" }));
  assert.ok(isSpam({ ...good, message: "http://a http://b http://c" }));
  assert.ok(!isSpam(good));
});
test("language detection and intent", () => {
  assert.equal(detectLanguage("שלום"), "he"); assert.equal(detectLanguage("Καλημέρα"), "el");
  assert.equal(detectLanguage("Привіт, їжак"), "uk"); assert.equal(detectLanguage("Привет"), "ru");
  assert.equal(detectLanguage("hello", "ro"), "ro");
  assert.equal(classify("I am a landlord"), "owner"); assert.equal(classify("אני בעלת דירה בניקוסיה"), "owner"); assert.equal(classify("אני בעל דירה"), "owner"); assert.equal(classify("there is a leak"), "maintenance");
});
test("reply is localised, RTL for Hebrew", () => {
  const l = enrich(validate({ ...good, name: "דנה", message: "שלום" }).lead, { pageLang: "he" });
  const r = buildReply(l); assert.equal(r.dir, "rtl"); assert.match(r.text, /דנה/);
});
test("handler: success forwards enriched payload", async () => {
  let sent; const fetchImpl = async (u, o) => { sent = JSON.parse(o.body); return new Response("ok"); };
  const res = await handle(req(good), env, { fetchImpl });
  assert.equal(res.status, 200); assert.equal(sent.lead.intent, "owner"); assert.equal(sent.auto_reply.to, "anna@example.com");
});
test("handler: wrong origin 403, bad input 422, spam fake-200 without forwarding, GET 405", async () => {
  let calls = 0; const fetchImpl = async () => { calls++; return new Response("ok"); };
  assert.equal((await handle(req(good, { origin: "https://evil.test" }), env, { fetchImpl })).status, 403);
  assert.equal((await handle(req({ ...good, email: "x" }), env, { fetchImpl })).status, 422);
  assert.equal((await handle(req({ ...good, _kleap_hp: "x" }), env, { fetchImpl })).status, 200);
  assert.equal((await handle(req(null, {}, "GET"), env, { fetchImpl })).status, 405);
  assert.equal(calls, 0);
});
test("handler: unconfigured 503, webhook failure 502", async () => {
  assert.equal((await handle(req(good), { ALLOWED_ORIGINS: env.ALLOWED_ORIGINS })).status, 503);
  assert.equal((await handle(req(good), env, { fetchImpl: async () => new Response("no", { status: 500 }) })).status, 502);
});
