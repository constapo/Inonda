# Lead intake

Turns a website form submission into an enriched lead and a localised auto-reply, then forwards both to a webhook.

```
form (contact / owners page) --POST JSON--> handler --> LEAD_WEBHOOK_URL
                                               |            (Zapier / Make / Composio / Slack)
                                               +-- validate, honeypot, origin check
                                               +-- language (en el he ro ru uk), intent (owner / tenant / maintenance / general), priority
                                               +-- auto-reply text in the lead's language
```

The webhook receiver does the last mile: create the CRM or Notion row, send the auto-reply email, alert you. That keeps every credential out of this repo.

## Config (environment, never committed)
| Var | Purpose |
|---|---|
| `ALLOWED_ORIGINS` | Comma list of your site origins. Other origins get 403. |
| `LEAD_WEBHOOK_URL` | Where enriched leads are POSTed. Unset returns 503. |

## Payload sent to the webhook
`{ lead: { name, email, phone, subject (defaults to the topic or "Website enquiry"), message, extra (address, type, units, occupancy, topic when sent), intent, language, priority, source_page, received_at }, auto_reply: { to, subject, text, dir } }`

## Deploy (not done yet)
1. Host `src/handler.js` as a Cloudflare Worker, Vercel or Netlify edge function (it is a standard `fetch` handler).
2. Set the two env vars.
3. Add `<script src="/form-hook.js" data-endpoint="https://YOUR-ENDPOINT" defer></script>` to the pages with the forms (contact and owners, in all six languages). The current forms have no submit action, so nothing is received today.

## Test
`npm test` (Node 20+, no dependencies).

## Before go-live
- Have a native speaker check the auto-reply wording in `src/replies.js`.
- Add a privacy notice and consent text near the form: leads are personal data (GDPR).
- Add rate limiting at the host (e.g. Cloudflare rules); this handler only does honeypot and size checks.
