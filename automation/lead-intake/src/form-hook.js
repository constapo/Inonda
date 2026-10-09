// Drop-in client script. Set data-endpoint on the script tag:
//   <script src="/form-hook.js" data-endpoint="https://leads.example.workers.dev" defer></script>
(() => {
  const endpoint = document.currentScript?.dataset.endpoint;
  if (!endpoint) return;
  document.addEventListener("submit", async (e) => {
    const form = e.target;
    if (!(form instanceof HTMLFormElement) || !form.querySelector('[name="message"]')) return;
    e.preventDefault();
    const data = Object.fromEntries(new FormData(form).entries());
    const btn = form.querySelector('[type="submit"]'); if (btn) btn.disabled = true;
    try {
      const r = await fetch(endpoint, { method: "POST", headers: { "content-type": "application/json" },
        body: JSON.stringify({ ...data, lang: document.documentElement.lang?.slice(0, 2), page: location.pathname }) });
      if (!r.ok) throw new Error(String(r.status));
      form.reset();
      alert(document.documentElement.lang?.startsWith("en") ? "Thank you — we will reply shortly." : "✓");
    } catch { alert("Sorry, something went wrong. Please email us directly."); }
    finally { if (btn) btn.disabled = false; }
  }, true);
})();
