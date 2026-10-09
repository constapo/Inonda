// Sends contact/owners form submissions to the lead-intake Worker.
// Inactive until the script tag's data-endpoint is set (see automation/lead-intake/ZAPIER.md).
(() => {
  const endpoint = document.currentScript?.dataset.endpoint;
  if (!endpoint) return;
  const lang = (document.documentElement.lang || "en").slice(0, 2);
  const T = {
    en: ["Thank you — we will reply shortly.", "Sorry, something went wrong. Please email us directly."],
    el: ["Ευχαριστούμε — θα σας απαντήσουμε σύντομα.", "Λυπούμαστε, παρουσιάστηκε σφάλμα. Στείλτε μας email απευθείας."],
    he: ["תודה — נחזור אליך בקרוב.", "מצטערים, אירעה שגיאה. אנא שלחו לנו מייל ישירות."],
    ro: ["Mulțumim — vă vom răspunde în curând.", "Ne pare rău, a apărut o eroare. Vă rugăm să ne scrieți direct pe email."],
    ru: ["Спасибо — мы скоро ответим.", "Извините, произошла ошибка. Пожалуйста, напишите нам на email."],
    uk: ["Дякуємо — ми скоро відповімо.", "Вибачте, сталася помилка. Будь ласка, напишіть нам на email."],
  };
  const [okMsg, errMsg] = T[lang] || T.en;
  document.addEventListener("submit", async (e) => {
    const form = e.target;
    if (!(form instanceof HTMLFormElement) || !form.querySelector('[name="message"]')) return;
    e.preventDefault();
    const data = Object.fromEntries(new FormData(form).entries());
    const btn = form.querySelector('[type="submit"]');
    if (btn) btn.disabled = true;
    try {
      const r = await fetch(endpoint, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ ...data, lang, page: location.pathname }),
      });
      if (!r.ok) throw new Error(String(r.status));
      form.reset();
      alert(okMsg);
    } catch {
      alert(errMsg);
    } finally {
      if (btn) btn.disabled = false;
    }
  }, true);
})();
