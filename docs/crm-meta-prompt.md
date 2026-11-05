# Meta Prompt — Inonda Command Center (CRM + AI Operations Hub)

> **How to use this file.** This file plus the 4 part files listed below are the master brief for building the app. Paste all five files in full
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

## Parts of this prompt (read all, in order)

- [`crm-meta-prompt/01-modules.md`](crm-meta-prompt/01-modules.md): sections 3
- [`crm-meta-prompt/02-ai.md`](crm-meta-prompt/02-ai.md): sections 4
- [`crm-meta-prompt/03-hosting-data-security.md`](crm-meta-prompt/03-hosting-data-security.md): sections 5, 6, 7
- [`crm-meta-prompt/04-delivery.md`](crm-meta-prompt/04-delivery.md): sections 8, 9, 10

---

## 11. Open questions for the owner (answer before Phase 1)

1. ~~What does Inonda do?~~ Answered: services from inonda.site, inonda.org and inonda.homes, focused on selling property services (see section 2).
2. ~~Who will use the app?~~ Answered: the owner and the requester/operator, both Admin (see section 2).
3. ~~Which accounts exist?~~ Answered: YouTube, Facebook, Instagram, TikTok and WhatsApp as linked on the sites. More networks are planned (see section 3.3).
4. ~~Accounting / bank?~~ Answered: own accounting module built from scratch; Eurobank Cyprus connected after the CRM is fully working; online from any device, computer as backup (see sections 3.6 and 5).
5. ~~AI providers / budget?~~ Answered: Claude is the only paid AI, plus Canva (design) this month; everything else is open-source, self-hosted on a VM (see 4.1 and 4.1b). Claude API: Option B (no API, app runs on open models) confirmed long-term. Still open: VM provider/budget.
6. ~~AI autonomy?~~ Answered: broad mandate for growth and visibility (local + international) and decision support. Three-level policy in section 4.2a.
7. ~~Domain?~~ Answered: free Wasmer subdomain, fully private (login required), moving to Inonda's own server later. Wasmer: account exists; create a company-email account to own the app.
8. ~~Day-one data?~~ Answered: everything related to the activity, including marketing tools and their buttons (see section 3.9). Still open: where past form submissions and client spreadsheets are kept today.
