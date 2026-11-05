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

Guiding principle (owner decision): **the AI has a broad mandate to grow Inonda's income
and visibility, locally in Cyprus and internationally, and to help staff make
decisions.** It acts on its own for growth and routine work. Only actions that commit
money, create legal obligations or can't be undone wait for a human. See the autonomy
policy in section 4.2a.

---

## 2. Business context

- Company: **Inonda LTD**, a registered Cyprus company based in Nicosia, serving all of
  Cyprus (Nicosia, Strovolos, Latsia, Aglantzia, Lakatamia, Engomi, Limassol, Larnaca,
  Protaras, Agia Napa). **Confirmed by owner:** the app covers exactly the activities on
  the company websites, and its focus is **selling services for properties**.
- Websites (all in EL / EN / RU / UK / HE / RO):
  - **inonda.site**: property management for landlords, investors, homeowners and
    tenants. Covers tenant communication, maintenance with 24/7 issue reporting and
    cost approval before work, move-in / routine / move-out inspections with photo
    records, rental pricing, and regular owner reports. Sales funnel: contact →
    free property assessment → management proposal → ongoing management.
    This repository holds this site.
  - **inonda.org**: contractor for maintenance, repairs and home transformation.
    - Maintenance: maintenance plans, air conditioning, roof waterproofing and damp.
    - Repairs: plumbing, electrical, handyman and urgent repairs.
    - Transformation: kitchens, bathrooms, full renovations, painting, gypsum, flooring
      and tiling, doors and windows, outdoor works and pergolas.
    - Sales funnel: free quote or site visit (also via WhatsApp) → itemised written
      quote → work → written workmanship warranty.
  - **inonda.homes**: a service estimator, the price-estimate entry point for leads.
- What this means for the CRM:
  - **Core records:** clients (owners, landlords, investors, tenants, businesses),
    properties, service requests or jobs, site visits, quotes, maintenance-plan and
    management contracts, inspections (with photos), invoices, and technicians or
    subcontractors.
  - **Main pipeline:** lead (website form, estimator, WhatsApp, phone, social) →
    assessment or site visit → quote or proposal → won/lost → job scheduled → done →
    invoice → warranty and follow-up → upsell into a maintenance plan or management.
  - **Lead routing:** each lead is tagged with the website it came from and the service
    line it is for.
- Users (confirmed): **2 users at launch**, the company owner and the app's
  requester/operator. Both get full **Admin** rights and both can approve AI actions.
  - Keep the RBAC system in place from day one, with ready-made roles that start
    unused: Manager, Office staff, Technician (mobile, sees only their jobs),
    Accountant (finance, read-only), Marketer. Adding staff later only needs an invite.
  - Small team, so keep onboarding light: no complex org setup. Every AI approval
    still records which of the two users approved it.
  - [CONFIRM later: should some actions need both people to approve (for example
    payments or deleting records), or is one approval enough?]
- Country & tax jurisdiction: **Cyprus** (Cyprus Tax Department, VAT, statutory audit).
- Currency: **EUR**.
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
- **Accounts that exist now** (confirmed by owner; linked on inonda.site, inonda.org and
  inonda.homes). These are the Phase 3 connectors:
  - **YouTube:** youtube.com/@InondaLTD (Data API v3: upload, metadata, Shorts, analytics).
  - **Facebook Page:** facebook.com/inondalimited (Meta Graph API).
  - **Instagram:** instagram.com/inondaltd. Needs an Instagram Business or Creator account
    linked to the Facebook Page so posts and Reels can be published.
  - **TikTok:** tiktok.com/@inonda26 (Content Posting API; needs TikTok app review before
    the app can post publicly).
  - **WhatsApp:** +357 94 091 613 and +357 94 091 616, the main lead channel on every
    site. Use the WhatsApp Business Platform (Cloud API) for the inbox, lead capture and
    templated replies. [CONFIRM: which number is sales and which is support, and whether
    the numbers are on the WhatsApp Business app today.]
  - **Websites:** inonda.site, inonda.org and inonda.homes. Send contact forms and
    estimator requests to the CRM by webhook, and read site analytics.
- **Planned expansion** (owner intends to grow marketing onto more networks): the connector
  design must make adding one a plug-in task. Likely next, in suggested order:
  1. Google Business Profile (local search and reviews in Cyprus).
  2. LinkedIn Company Page (investors and B2B clients).
  3. X, Threads, Pinterest (before/after renovation photos), Telegram and Viber
     (popular with RU/UA-speaking clients).
  4. Property portals such as Bazaraki [CONFIRM which ones].
- Note: the copy of the site in this repository still has placeholder links
  (`facebook.com/`, `instagram.com/`, `linkedin.com/`) instead of the real profiles, and
  only one WhatsApp number. Fix this in a separate website task.
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

### 3.6 Accounting & finance — built in-house (confirmed)
Owner decision: **no third-party accounting software.** Inonda builds its own accounting
module inside the app, with a dashboard designed from scratch around how Inonda works.
It must not copy the usual Xero or QuickBooks layout.
- **Dashboard concept: answers first, not ledgers first.**
  - Cards: cash in the bank today, what clients owe us (by job and by property), what we
    owe suppliers and subcontractors, profit per job, profit per service line
    (management / maintenance / repairs / renovation), VAT due this period, and the
    cash forecast for the next 30, 60 and 90 days.
  - Drill down from any card to the transactions behind it.
- **Core engine: proper double-entry bookkeeping** behind the simple UI.
  - Chart of accounts, journals, invoices with sequential numbering, credit notes,
    expenses, supplier bills, and fixed assets.
  - Entries can't be deleted: corrections are reversals. Every change is logged and
    periods can be locked.
- **Ties to the CRM:** quote → job → invoice → payment all link to one client and
  property. Job costing covers materials, subcontractor and labour hours against the
  quoted price. Management contracts get recurring invoices.
- **Expenses:** photo of a receipt from the phone → OCR → AI suggests category and VAT
  → human approves.
- **Cyprus compliance** [CONFIRM every rule with Inonda's accountant/auditor before go-live]:
  - VAT returns to the Cyprus Tax Department, with standard and reduced rates (the
    reduced rate can apply to some renovation work).
  - VIES / reverse charge where relevant.
  - Annual statutory financial statements: Cyprus companies are audited, so give the
    auditor read-only access and exports.
  - Corporate tax figures, and records kept for at least 6 years.
  - Watch for upcoming EU/Cyprus e-invoicing mandates (ViDA). The invoice data model
    must be ready for structured e-invoices (EN 16931 / UBL).
- **AI bookkeeper:** categorises, reconciles, flags duplicates and anomalies, and drafts
  entries. It **always needs human approval** and never posts to the ledger by itself.
- **Bank: Eurobank Cyprus (business account).** Connect it **after the CRM is fully
  working** (a later phase).
  - Preferred: the bank's PSD2 / Open Banking API, read-only (balances and
    transactions), through Eurobank's developer portal or a licensed aggregator
    [CONFIRM what Eurobank Cyprus offers].
  - Fallback from day one: import statement files (CSV / MT940 / CAMT.053).
  - Never store online-banking passwords. No payment initiation unless the owner
    explicitly decides on it later.
- **Reports:** P&L, balance sheet, cash flow, VAT report, receivables and payables aging,
  job and service-line profitability, budget vs actual, and marketing ROI per channel.

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

**Budget rule (confirmed):** the only paid AI is Claude. Everything else must be
**open-source, self-hosted** models running on Inonda's own "virtual computer" (a cloud VM),
reached by the app over a private API. Claude is the lead; open models do the bulk work.

| Agent | Model (default) | Does | Needs approval for |
|---|---|---|---|
| **Lead orchestrator** | Claude | Plans, routes, reviews specialist output, handles hard reasoning | Anything external |
| CRM assistant | Open LLM (e.g. Qwen / Llama / Mistral 7–14B) | Dedup, summarise history, suggest next step | Bulk edits, deletes |
| Inbox triage | Open LLM (small, fast) | Classify messages and language, draft replies, create leads | Sending replies |
| Marketing / content | Open LLM drafts → Claude polishes the final | Briefs, scripts, captions in 6 languages, hashtags | Publishing |
| Video producer | FFmpeg pipeline (reuse `scripts/video-ad/`) + open TTS (Piper / XTTS) + Whisper subtitles + open image model (FLUX.1-schnell / SDXL) | Stock-footage or photo edits, voice-over, subtitles, thumbnails; open video models (Wan / LTX-Video) only if a GPU is available | Publishing |
| Publisher | Rules (no LLM) + small open LLM | Schedules and posts through connectors, retries | First post per channel, then per policy |
| Documents | Open LLM drafts → Claude reviews contracts | Quotes, offers, contracts, letters from templates | Sending / signing |
| Bookkeeper | Rules + OCR (Tesseract / PaddleOCR) + open LLM | Read receipts, categorise, reconcile, flag anomalies | Every ledger change |
| Analyst | Claude (SQL results passed in, no raw data dumps) | Weekly briefing, decision support | — (read-only) |

**Canva (paid this month, confirmed):** use it as the design tool next to the open
models. Connect it through the **Canva Connect API** (OAuth). Use it for brand kit,
templates, designs, exports to PNG/MP4/PDF, and pulling finished designs into the media
library for the Publisher.
- Some features, such as Autofill / brand templates by API, need a higher Canva plan
  [CONFIRM plan].
- Build it as an optional connector. If the subscription lapses, the open pipeline
  (FFmpeg + FLUX/SDXL + Piper) keeps working.

### 4.1b The AI "virtual computer" (self-hosted models)
- **Separate from Wasmer.** Wasmer Edge cannot run LLMs, so the models run on their own
  cloud VM (Linux).
  - Start small with a CPU-only VPS: 8–16 vCPU and 32 GB RAM runs quantised 7–8B models,
    Whisper, Piper and OCR at modest speed.
  - Add a rented GPU later, by the hour or month, only if speed or video generation
    needs it.
  - [CONFIRM: provider and budget for the VM.]
- **Runtime:** Ollama or llama.cpp server, with vLLM if a GPU is added. It exposes an
  **OpenAI-compatible API** behind auth and private networking (Tailscale/WireGuard or
  mTLS), so the app's `llm.generate()` can switch between Claude and local models per
  agent.
- **Queue:** the app on Wasmer puts jobs on a queue (e.g. Redis/Postgres-based). A worker
  on the VM picks them up, runs the model or FFmpeg, uploads results to object storage,
  and calls back. No long tasks run inside a Wasmer request.
- **Licences:** use only models whose licence allows commercial use (e.g. Apache-2.0 or
  MIT; Llama and Gemma licences have conditions). Record each model's licence in the
  admin panel. Check voice-cloning and image-model terms before use.
- **Data stays private:** client data sent to local models never leaves Inonda's VM.
  When data goes to Claude, send only the minimum needed (no full client lists, mask
  IBANs and ID numbers).
- **Claude usage — important:** a Claude chat subscription (Pro/Max) does **not** cover
  the app calling Claude automatically. That needs the **Anthropic API**, billed
  separately per use.
  - **Decision (confirmed, long-term plan): Option B.** No Anthropic API in the app.
    Claude is used by the two users through Claude Code / chat to plan, build, review
    and analyse. The app itself runs **fully on open-source self-hosted models**.
  - So every in-app agent marked "Claude" above runs on the best available local model.
    Human review in Claude chat replaces automatic Claude calls: for example, export
    the weekly data summary and ask Claude for the briefing.
  - Keep `llm.generate()` provider-agnostic so an API provider *could* be added later
    without code changes, but it is off by default.
- **Fallback:** if the VM is down, the app keeps working (CRM, accounting, manual
  publishing) and AI jobs wait in the queue.

### 4.2a Autonomy policy (confirmed: broad mandate for growth)
Owner instruction: *"do whatever needs to be done for the company to grow its income and
visibility, locally and internationally, and assist staff on decision making."*
Three levels, each one switchable per action in Admin:

**Level 1 — Auto** (AI acts, logs it, and reports in the daily digest)
- Lead handling:
  - Instant first reply to new leads on WhatsApp, web forms and DMs, in the lead's
    language.
  - Ask qualifying questions and create or update the contact, property and deal.
  - Offer site-visit slots from the shared calendar.
- Follow-ups:
  - Follow up quotes with no answer, and ask for reviews after a finished job.
  - Remind clients about maintenance plans and send seasonal offers (AC servicing
    before summer, waterproofing before winter). Only to contacts who gave marketing
    consent.
- Content and channels:
  - Plan the content calendar, write, produce and **publish** posts, Reels, Shorts and
    videos on the connected channels, in all 6 languages.
  - Reply to comments, answer FAQs, and update profiles and descriptions.
  - SEO and AEO work: suggestions and drafts for inonda.site, inonda.org and
    inonda.homes, plus blog or landing pages for new areas and languages.
- Growth research:
  - Track competitors and market trends (local and international), and keep target
    lists for international owners and investors (e.g. buyers from Israel, Romania,
    Ukraine, Russia, Greece).
  - Find partner opportunities with estate agents, developers and relocation services.
- CRM and staff support: data cleanup, deduplication, tagging, lead scoring, task
  creation for staff, the weekly growth report, and decision briefings with options,
  numbers and a recommendation.
- Accounting routine: categorise transactions, match bank lines, send standard
  invoice-payment reminders, and flag anomalies.

**Level 2 — Auto with an undo window** (AI prepares, waits 2 hours [adjustable], then
sends unless a human stops it)
- Sending a quote or proposal that uses the approved price list, with no custom
  discount.
- Booking a site visit or job into a technician's calendar.
- Starting a new marketing campaign or opening a new social channel or profile.
- Replying to a negative review or a client complaint.

**Level 3 — Always needs explicit human approval**
- Spending money: ad budgets, subscriptions, purchases, paying suppliers.
- Prices or discounts outside the approved price list, and any contract, agreement or
  legal letter.
- Posting entries to the ledger, VAT returns, anything sent to the tax office or
  auditor, and bank connection settings.
- Deleting records, bulk-changing client data, exporting personal data outside the
  app.
- Statements about the company's licences, guarantees, legal status or prices that
  aren't already approved and published.

**Hard limits** (never, whatever the setting):
- No spam or bought contact lists.
- No messages to people without a lawful basis or marketing consent (GDPR).
- WhatsApp outside its 24-hour window only with approved templates.
- No fake reviews, accounts or engagement, and no breaking platform rules.
- No pretending to be a human when someone sincerely asks.
- No sharing client data with third parties.

**Controls:**
- A daily digest of everything the AI did.
- A big **pause all AI** switch.
- Per-channel daily limits on posts and messages.
- The AI learns from approvals, rejections and results: which posts, offers and
  channels bring paying clients.

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

## 11. Open questions for the owner (answer before Phase 1)

1. ~~What does Inonda do?~~ Answered: services from inonda.site, inonda.org and inonda.homes, focused on selling property services (see section 2).
2. ~~Who will use the app?~~ Answered: the owner and the requester/operator, both Admin (see section 2).
3. ~~Which accounts exist?~~ Answered: YouTube, Facebook, Instagram, TikTok and WhatsApp as linked on the sites. More networks are planned (see section 3.3).
4. ~~Accounting / bank?~~ Answered: own accounting module built from scratch; Eurobank Cyprus connected after the CRM is fully working; online from any device, computer as backup (see sections 3.6 and 5).
5. ~~AI providers / budget?~~ Answered: Claude is the only paid AI, plus Canva (design) this month; everything else is open-source, self-hosted on a VM (see 4.1 and 4.1b). Claude API: Option B (no API, app runs on open models) confirmed long-term. Still open: VM provider/budget.
6. ~~AI autonomy?~~ Answered: broad mandate for growth and visibility (local + international) and decision support. Three-level policy in section 4.2a.
7. ~~Domain?~~ Answered: free Wasmer subdomain, fully private (login required), moving to Inonda's own server later. Wasmer: account exists; create a company-email account to own the app.
8. Data to import on day one (spreadsheets, old CRM, contact lists)?
