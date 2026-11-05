# Meta Prompt — Inonda Command Center (CRM + AI Operations Hub)

> **How to use this file.** This is the master brief for building the app. Paste it in full
> as the first message of every build session (Claude Code, another AI coding agent, or a
> human developer). Items marked **[CONFIRM]** are decisions the owner still has to make —
> the builder must ask about them, not guess. Keep this file as the single source of truth:
> when a decision is made, edit it here.

---

## 1. Role and mission

You are the **lead architect and engineer** for *Inonda Command Center*, an internal web
app for the company Inonda. You are also the design authority for the **AI layer** inside
it, where a lead AI orchestrator (Claude) coordinates specialist AI models.

The app must let the company:

1. **Store and edit** all business records in one place (CRM: contacts, companies,
   properties/assets, deals, tasks, documents, invoices, expenses).
2. **Stay live-connected** to the company websites and every social / video channel the
   company uses — existing ones and new ones added later — reading data in and pushing
   content out.
3. **Use AI agents** to help control company activity: draft and produce videos, publish
   them to social media and video hosts (YouTube etc.), write documents, prepare
   accounting entries, and support decisions with data.
4. **Run on Wasmer.io** (Wasmer Edge) as a new app.

Guiding principle: **AI proposes, humans approve.** Nothing that spends money, publishes
publicly, sends to a client, or touches the books happens without an explicit approval
step by an authorised person, unless the owner has switched that specific action to
"auto" in settings.

---

## 2. Business context [CONFIRM all]

- Company: **Inonda** — current public site in this repository (static HTML, languages
  EN / EL / HE / RO / RU / UK). Business domain: [CONFIRM: property management /
  real estate services / other].
- Users: [CONFIRM: number of staff, roles — owner, manager, agent, accountant, marketer,
  external accountant read-only].
- Countries of operation & tax jurisdiction: [CONFIRM: e.g. Greece → VAT, myDATA/AADE e-books].
- Currency: [CONFIRM: EUR primary, others?].
- UI languages: English first, then Greek; architecture must allow all six site languages.
- Existing tools to integrate or replace: [CONFIRM: accounting software, email provider,
  calendar, cloud drive, any current CRM or spreadsheets to import].

---

## 3. Scope — modules

### 3.1 Dashboard (home)
- KPI tiles: leads this week, open deals + value, revenue MTD vs last month, unpaid
  invoices, cash position, social reach/engagement 7 days, website visits, pending
  approvals.
- "Needs your decision" queue: every AI proposal waiting for approval.
- Activity feed (human + AI actions, with who/what/when).
- Content calendar preview (scheduled posts/videos).
- Alerts: failed publish, expired channel token, overdue invoice, unusual expense.

### 3.2 CRM core
- **Contacts & companies**: full profile, tags, source (website form, social DM, referral,
  manual), consent status (GDPR), timeline of every interaction.
- **Properties / assets** [CONFIRM if relevant]: address, owner, status, documents, photos.
- **Deals / pipeline**: customisable stages, kanban + table view, value, probability,
  next step, owner.
- **Tasks & calendar**: assign to people *or* AI agents, due dates, reminders.
- **Inbox**: unified view of website form submissions, email, and social DMs/comments
  (where channel APIs allow), linkable to contacts.
- Full **create / edit / delete / bulk edit / import CSV / export CSV** on every entity.
- Audit history on every record (field-level: old value → new value, by whom).

### 3.3 Channels hub ("live connections")
- **Connector registry**: each channel is a plugin with a common interface
  (`connect`, `refreshToken`, `fetchMetrics`, `fetchInbox`, `publish`, `deletePost`,
  `health`). Adding a new network later = adding one connector, no core changes.
- Initial connectors [CONFIRM which accounts exist]:
  - Websites: Inonda site(s) — contact-form webhook into CRM, analytics (GA4 or
    privacy-friendly alternative [CONFIRM]), blog/page publishing if CMS-backed.
  - YouTube (Data API v3), Facebook Pages + Instagram Business (Meta Graph API),
    LinkedIn (Company Pages), TikTok (Content Posting API), X, Pinterest, Threads,
    Google Business Profile, Telegram/WhatsApp Business [CONFIRM].
- Optional aggregator fallback (e.g. Ayrshare / Metricool / Zapier) for networks whose
  native API access is not yet approved — behind the same connector interface.
- Per-channel status page: connected / token expiring / error, last sync, rate-limit use.
- Respect each platform's terms: official APIs only, no scraping of logged-in pages, no
  automated actions the platform forbids.

### 3.4 Content & video studio
- Content calendar (month/week), drafts → review → approved → scheduled → published →
  measured.
- Brief → script → shot list → assets → render → captions/subtitles → thumbnail →
  multi-format export (16:9, 9:16, 1:1) → per-channel caption & hashtags.
- Reuse what already exists in this repo (`video-ad/`: shot plan, Greek subtitles,
  assembly script) as the first template.
- Media library with tags, rights/licence info, and usage history.
- Every published item links back to its metrics so the AI can learn what works.

### 3.5 Documents
- Templates (contracts, offers, letters, reports) with merge fields from CRM.
- AI drafting with tracked changes; human approval before sending.
- E-signature integration [CONFIRM provider], versioning, PDF export, storage per
  contact/deal.

### 3.6 Accounting & finance
- Invoices (issue, send, track paid/unpaid, reminders), expenses with receipt upload +
  OCR, bank-feed import [CONFIRM bank/CSV], categories / chart of accounts.
- Sync with external accounting system or local e-invoicing obligations [CONFIRM — e.g.
  myDATA in Greece]; the app is **not** the legal book of record unless explicitly decided.
- AI bookkeeper: suggests categorisation, flags duplicates/anomalies, drafts journal
  entries — **always pending human approval**, never posts to the ledger by itself.
- Reports: P&L, cash flow, receivables aging, budget vs actual, per-channel marketing ROI.

### 3.7 Decision support
- "Ask the company" chat: natural-language questions over CRM, finance and channel data
  ("Which channel brought the most paying clients this quarter?").
- Weekly AI briefing: what changed, risks, 3 recommended actions with the data behind
  each, and an estimate of confidence.
- Scenario tool: simple what-if on budget, pricing, hiring, ad spend.
- Every AI answer cites the records/queries it used; no invented numbers.

### 3.8 Admin
- Users, roles, permissions (RBAC) per module and per action (view/edit/approve/delete).
- AI agent settings: which agents are on, which actions are "approval required" vs
  "auto", monthly AI budget caps per agent.
- API keys / secrets management (stored encrypted, never shown in full after save).
- Data export of everything (no lock-in), backups, retention policies.

---

## 4. AI architecture

### 4.1 Agents (each = role + allowed tools + approval policy + budget)

| Agent | Model (default) | Does | Needs approval for |
|---|---|---|---|
| **Lead orchestrator** | Claude (latest Opus/Sonnet) | Understands the request, plans, routes to specialists, merges results, explains | Anything external |
| CRM assistant | Claude Haiku/Sonnet | Dedup, enrich, summarise contact history, suggest next step | Bulk edits, deletes |
| Marketing / content | Claude Sonnet | Briefs, scripts, captions, hashtags per channel, content calendar | Publishing |
| Video producer | Claude + video/image/voice models (e.g. Veo/Kling/Runway, ElevenLabs) [CONFIRM providers] | Storyboards, generates/assembles clips, subtitles, thumbnails | Rendering above cost cap; publishing |
| Publisher | rules + Claude | Schedules and posts via connectors, retries, reports results | Every first post per channel; then per policy |
| Documents | Claude Sonnet | Drafts contracts/letters from templates + CRM data | Sending / signing |
| Bookkeeper | Claude Sonnet | Categorise, reconcile, anomaly detection, draft entries | Every ledger change |
| Analyst | Claude Opus | Weekly briefing, decision support, forecasts | — (read-only) |
| Inbox triage | Claude Haiku | Classify incoming messages, draft replies, create leads | Sending replies |

### 4.2 Rules for the AI layer
- **Provider abstraction**: one internal `llm.generate()` / `media.generate()` interface so
  models can be swapped per agent without code changes.
- **Tool-calling only through the app's own API** with the calling user's permissions —
  agents can never do more than the human who triggered them.
- **Approval queue** object: `{agent, action, payload, preview, cost_estimate, risk,
  requested_by, status}`; approve / edit / reject with comment; rejection feedback is
  stored and fed back into that agent's prompt context.
- **Full audit log** of prompts, tool calls, outputs, cost and approver.
- **Cost control**: per-agent monthly budget, per-job cost estimate shown before any
  paid generation (especially video), hard stop at the cap.
- **Grounding**: answers about company data must come from queries (RAG over documents
  + SQL over records); show sources; say "I don't know" when data is missing.
- **Safety**: prompt-injection defence for content coming from emails, DMs, comments and
  web pages (treat as data, never as instructions); PII minimisation in prompts.
- **Memory**: company knowledge base (brand voice, price lists, FAQs, policies,
  past-performance notes) editable by the owner, versioned.

---

## 5. Hosting & technical constraints — Wasmer.io

- Target: **Wasmer Edge** app (new app, own subdomain first, custom domain later
  [CONFIRM domain]).
- Before choosing the stack, the builder must **check current Wasmer Edge docs** for:
  supported runtimes (Python/PHP/JS-WinterJS/static/WASIX), managed database options,
  persistent volumes, cron/scheduled jobs, request time limits, outbound HTTP, secrets,
  and pricing. Record the findings in this section.
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
   production deploy on custom domain, user training notes.

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

## 11. Open questions for the owner (answer before Phase 1)

1. What exactly does Inonda do, and which records matter most (clients, properties,
   projects…)?
2. Who will use the app and with which permissions?
3. Which social/video accounts exist today, and which are priorities?
4. Which accounting software / bank / tax obligations must we connect to?
5. Which AI and video providers do you already pay for, and what monthly AI budget?
6. Which actions may AI do automatically, and which always need your approval?
7. Domain for the app (e.g. `app.inonda…`) and do you already have a Wasmer account/team?
8. Data to import on day one (spreadsheets, old CRM, contact lists)?
