# Inonda Command Center — meta prompt (part)

> Part of [`../crm-meta-prompt.md`](../crm-meta-prompt.md). Read the main file first.

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

### 3.9 Day-one data import (confirmed: import everything related to the activity)
Owner instruction: import **all data related to Inonda's activity, including the marketing
tools and the buttons on them.** Phase 2 ends with this import done and verified.
- **Websites** (inonda.site, inonda.org, inonda.homes):
  - Services, service areas, FAQs and all page text in the 6 languages, imported as the
    **service catalogue** and the AI's knowledge base.
  - Past form submissions and estimator requests, where they are stored (form provider
    or mailbox).
- **Marketing buttons and entry points.** Every call-to-action on every site and
  language becomes a tracked **lead source** in the CRM:
  - "Free Quote", "Request a Free Property Assessment", "Book a site visit"
  - WhatsApp buttons for +357 94 091 613 and +357 94 091 616
  - phone and email links
  - the Facebook, Instagram, TikTok and YouTube icons
  - the estimator on inonda.homes
  Each button gets a stable ID plus UTM parameters, so a lead shows which site,
  language, page and button it came from. The dashboard shows clicks → leads → won
  jobs → revenue per button.
  The website repos get small edits to add the tracking. These are website changes, so
  they get their own review.
- **Social and video channels:**
  - Profile details and the history of posts, videos and Reels, with their metrics.
  - Followers and engagement history where the API allows it.
  - Comments and DMs that are still open, imported as leads or conversations.
  - Sources: YouTube @InondaLTD, Facebook inondalimited, Instagram inondaltd,
    TikTok @inonda26.
- **WhatsApp:**
  - Contacts and chat history from both numbers, imported as contacts and an activity
    timeline. Use the WhatsApp chat export or the Business Platform, with consent noted.
- **Canva:** the brand kit (logo, colours, fonts), templates and existing designs, into
  the media library.
- **Existing media:** the ad video, shot plan, subtitles and stock-footage scripts in
  this repo (`video-ad/`, `scripts/video-ad/`), and all photos and videos of past jobs.
- **Business records**, from whatever exists (spreadsheets, email, phone, paper scans):
  - clients and their properties, past and current jobs, quotes, invoices and payments
  - management contracts, maintenance plans and inspection reports
  - suppliers, technicians and subcontractors, and the price list
- **How the import works:**
  1. Import into a staging area first. The AI maps the columns, then dedupes and links
     records.
  2. A human reviews and approves the merge.
  3. Every imported record keeps its source and import date.
  4. Each source has its own re-runnable importer.
  - [CONFIRM: where past form submissions and client spreadsheets are kept today.]

