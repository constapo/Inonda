# Inonda Command Center — meta prompt (part)

> Part of [`../crm-meta-prompt.md`](../crm-meta-prompt.md). Read the main file first.

## 8. Delivery plan (phases — each ends with a working, deployed increment)

0. **Discovery** — answer every [CONFIRM], verify Wasmer capabilities, list channel
   accounts + API access status, pick stack. Output: updated version of this file.
1. **Foundation** — repo structure, auth, RBAC, DB + migrations, audit log, deploy
   pipeline to Wasmer staging, empty dashboard shell, i18n.
2. **CRM core** — contacts, companies, deals, tasks, import/export, website form →
   lead webhook.
3. **Channels hub v1** — connector interface + 2–3 priority channels (likely YouTube,
   Facebook/Instagram, website); metrics into dashboard.
4. **AI layer v1** — orchestrator, provider abstraction, approval queue, audit, cost caps;
   CRM assistant + inbox triage + marketing agent.
5. **Content & video studio** — calendar, drafts, video pipeline with external rendering,
   publisher agent with approvals.
6. **Documents** — templates, AI drafting, e-signature.
7. **Accounting** — invoices, expenses/OCR, bank import, bookkeeper agent, reports,
   external accounting / e-invoicing sync.
8. **Decision support** — analyst agent, weekly briefing, scenarios.
9. **Hardening & go-live** — security review, load test, backups/restore drill,
   production deploy (Wasmer subdomain, private mode), user training notes; later migration to Inonda's own server.

---

## 9. Definition of done (per feature)

- Acceptance criteria written before coding and met.
- Unit + integration tests pass; critical flows have an end-to-end test.
- Permissions checked (a user without rights gets 403, an AI agent likewise).
- Audit log entries present; AI actions show in approval queue where required.
- Works on mobile width; translated strings present (EN + EL minimum).
- Deployed to staging on Wasmer and smoke-tested; changelog updated.

---

## 10. How the builder must work

1. Start each session by reading this file and the latest changelog.
2. Ask about any [CONFIRM] item that blocks the current phase — batch the questions in
   one message.
3. Propose a short plan (files, data changes, tests) before writing code for a phase.
4. Never commit secrets; use Wasmer secrets / environment variables.
5. Never connect a real social account, send real emails, or spend on paid AI/video
   generation without the owner's explicit OK in the session.
6. Prefer official SDKs and APIs; check current API docs (they change often) rather
   than relying on memory.
7. Small, reviewable commits; keep this document updated when decisions change.

---

