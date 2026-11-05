# Inonda Command Center — meta prompt (part)

> Part of [`../crm-meta-prompt.md`](../crm-meta-prompt.md). Read the main file first.

## 5. Hosting & technical constraints — Wasmer.io

- Target: **Wasmer Edge** app on the **free Wasmer subdomain** (confirmed; no custom
  domain for now). Wasmer is the **temporary home** until Inonda provides its own
  server.
- **Wasmer account (confirmed):** an account already exists, and a new one can be made
  with the company email. Recommended: create the **company-owned** account with the
  company email and host the app under its namespace or team. Invite both users as
  members, each with their own login and 2FA, so ownership stays with Inonda LTD.
  Keep the recovery email and 2FA backup codes in the company password vault.
- **Private mode (confirmed): internal tool for company staff only.**
  - Sharing the link is how people find the app, **not** how they get in: anyone who
    has the URL must still sign in.
  - Accounts are invite-only (no public sign-up), with 2FA for both admins, short
    sessions, and login-attempt limits.
  - Every page and API requires auth; only health checks and webhook endpoints stay
    open, and those verify signatures.
  - Search engines are blocked (`noindex` header and meta tag, `robots.txt` disallow
    all) and the URL appears nowhere public.
  - Webhooks from the websites, WhatsApp and Meta use secret tokens or signature
    checks.
  - Optional later: limit access to known IPs or devices.
- **Built to move (confirmed: will migrate to Inonda's own server).**
  - No Wasmer-only features in business logic. Use standard Postgres, S3-compatible
    storage and a plain HTTP app, also packaged as a Docker image.
  - All config comes from environment variables.
  - A migration runbook: export DB and files → import on the new server → switch the
    URL → verify → keep Wasmer read-only for one week.
  - The AI VM (section 4.1b) can later be the same server.
- Before choosing the stack, the builder must **check current Wasmer Edge docs** for:
  supported runtimes (Python/PHP/JS-WinterJS/static/WASIX), managed database options,
  persistent volumes, cron/scheduled jobs, request time limits, outbound HTTP, secrets,
  and pricing. Record the findings in this section.
- **Access model (confirmed):** the app runs **online** and works from any device (phone,
  tablet, laptop) in the browser. Build it as a responsive **PWA** that can be installed
  on phones and desktops.
- **Computer as backup (confirmed):**
  - Automatic encrypted backups (database dump + files) every night, downloaded to the
    owner's computer, plus an off-site copy.
  - A one-click "export everything" (CSV + PDF + JSON) to the computer.
  - A documented restore procedure, tested every quarter.
  - Optional: a read-only offline copy of key data on the computer for when the
    internet is down.
- Expected split (adjust after the check):
  - **On Wasmer**: web UI, API, auth, CRM database access, webhooks, light AI calls
    (LLM APIs are just HTTPS calls).
  - **Off Wasmer (external services)**: database if Wasmer's managed DB doesn't fit
    [e.g. managed Postgres], object storage for media (S3-compatible / Cloudflare R2),
    long-running jobs (video rendering, bulk sync) on a queue + worker or a hosted
    rendering/AI API, e-mail sending provider.
- Suggested stack [CONFIRM after Wasmer check]: TypeScript or Python backend, REST/JSON
  API with OpenAPI spec, Postgres-compatible DB, React or HTMX front end, Tailwind,
  i18n from day one.
- Infra as code / repeatable deploy: `wasmer.toml` + `app.yaml` committed, CI deploys
  on merge to main, separate **staging** and **production** apps.

---

## 6. Data model (starting point — refine in design phase)

`Organization, User, Role, Permission, Contact, Company, Property[CONFIRM], Deal,
PipelineStage, Activity, Task, Note, Document, DocumentTemplate, MediaAsset,
ContentItem, ContentVariant(per channel), Channel, ChannelConnection, PublishJob,
ChannelMetric, InboxMessage, Invoice, InvoiceLine, Expense, Receipt, BankTransaction,
Account(chart), JournalEntryDraft, Budget, AIAgent, AIJob, ApprovalRequest, AuditLog,
KnowledgeItem, Secret, WebhookEvent`

Every table: `id (uuid), org_id, created_at/by, updated_at/by, deleted_at` (soft delete).
Money stored as integer minor units + currency code. All times UTC, shown in user TZ.

---

## 7. Non-functional requirements

- **Security**: SSO/OAuth login + 2FA for admins, RBAC, encrypted secrets and channel
  tokens, HTTPS only, CSRF/XSS/SQLi protection, rate limiting, dependency scanning,
  least-privilege API scopes on every social connector.
- **Privacy/GDPR**: consent tracking, data subject export/delete, data processing
  register, EU data residency where possible [CONFIRM], DPA with every AI/vendor.
- **Reliability**: idempotent publish jobs, retries with backoff, dead-letter queue,
  daily backups + tested restore, health checks, error monitoring.
- **Performance**: dashboard < 2 s, lists paginated, metrics cached and synced on schedule.
- **Accessibility**: WCAG 2.1 AA. **Mobile-friendly** (owner approves from phone).
- **Observability**: structured logs, AI cost dashboard, connector health dashboard.
- **Code quality**: files < 500 lines, tests for every module, typed code, OpenAPI docs,
  `npm run build && npm test` (or equivalent) must pass before each commit.

---

