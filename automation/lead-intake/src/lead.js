// Pure functions: validate, classify and enrich a website lead. No I/O.
export const LANGS = ["en", "el", "he", "ro", "ru", "uk"];

const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

export function detectLanguage(text, pageLang) {
  if (LANGS.includes(pageLang)) return pageLang;
  if (/[֐-׿]/.test(text)) return "he";
  if (/[Ͱ-Ͽ]/.test(text)) return "el";
  if (/[іїєґІЇЄҐ]/.test(text)) return "uk";
  if (/[Ѐ-ӿ]/.test(text)) return "ru";
  if (/[ăâîșțĂÂÎȘȚ]/.test(text)) return "ro";
  return "en";
}

const INTENTS = [
  ["owner", /landlord|owner|my (property|apartment|house|flat)|manage my|management fee|rental income|ιδιοκτ|בעל דירה|נכס|proprietar|владел|собственик|власник/i],
  ["tenant", /tenant|rent (a|an)|looking for (a|an) (flat|apartment|house)|viewing|ενοικιαστ|שוכר|chiriaș|арендатор|снять|орендар/i],
  ["maintenance", /repair|leak|broken|maintenance|plumb|electric|βλάβη|תיקון|reparați|ремонт|протеч/i],
];

export function classify(text) {
  for (const [name, re] of INTENTS) if (re.test(text)) return name;
  return "general";
}

export function validate(input) {
  const errors = [];
  const v = (k) => String(input?.[k] ?? "").trim();
  const lead = { name: v("name"), email: v("email").toLowerCase(), phone: v("phone"), subject: v("subject"), message: v("message") };
  if (!lead.name || lead.name.length > 120) errors.push("name");
  if (!EMAIL.test(lead.email) || lead.email.length > 254) errors.push("email");
  if (lead.phone && !/^[+\d][\d\s().-]{5,24}$/.test(lead.phone)) errors.push("phone");
  if (!lead.subject || lead.subject.length > 200) errors.push("subject");
  if (!lead.message || lead.message.length > 5000) errors.push("message");
  // Headers/newline injection guard for anything that ends up in an email header.
  if (/[\r\n]/.test(lead.name + lead.email + lead.subject)) errors.push("newline");
  return { ok: errors.length === 0, errors, lead };
}

export function isSpam(input) {
  if (String(input?._kleap_hp ?? input?.website ?? "").trim() !== "") return true; // honeypot
  const links = (String(input?.message ?? "").match(/https?:\/\//gi) || []).length;
  return links > 2;
}

export function enrich(lead, { pageLang, page, now = new Date() } = {}) {
  const text = `${lead.subject}\n${lead.message}`;
  const intent = classify(text);
  return {
    ...lead,
    intent,
    language: detectLanguage(text, pageLang),
    priority: intent === "maintenance" ? "high" : intent === "owner" ? "high" : "normal",
    source_page: page || "",
    received_at: now.toISOString(),
  };
}
