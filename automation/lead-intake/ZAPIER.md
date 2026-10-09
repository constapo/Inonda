# Zapier setup (Webhooks by Zapier -> your tools)

Needs a Zapier plan that includes Webhooks by Zapier (a premium app).

## 1. Create the Zap
1. **Trigger:** Webhooks by Zapier -> **Catch Hook**. Leave "Pick off a Child Key" empty. Copy the **Custom Webhook URL**. This is your `LEAD_WEBHOOK_URL`.

## 2. Deploy the Worker (Cloudflare)
```
cd automation/lead-intake
npm install
npx wrangler login
# edit wrangler.toml: ALLOWED_ORIGINS = "https://your-real-site"  (several: comma separated)
npx wrangler secret put LEAD_WEBHOOK_URL      # paste the Zapier URL when prompted
npx wrangler deploy
```
Wrangler prints the Worker URL (`https://inonda-lead-intake.<account>.workers.dev`). Add a custom domain later in the Cloudflare dashboard.

## 3. Send a test lead (so Zapier learns the fields)
```
curl -X POST https://inonda-lead-intake.<account>.workers.dev \
  -H 'origin: https://your-real-site' -H 'content-type: application/json' \
  -d '{"name":"Test","email":"you@example.com","subject":"Test","message":"I am a landlord in Nicosia","lang":"en","page":"/contact"}'
```
In Zapier, "Test trigger" and pick the record. Fields arrive flattened, e.g. `lead__name`, `lead__intent`, `auto_reply__text`.

## 4. Actions (add the ones you want)
| Step | App / action | Map |
|---|---|---|
| Auto-reply | Gmail (or Outlook) -> Send Email | To `auto_reply__to`, Subject `auto_reply__subject`, Body `auto_reply__text` |
| Alert | Slack -> Send Channel Message | `lead__priority`, `lead__intent`, `lead__name`, `lead__subject`, `lead__message`, `lead__phone` |
| Record | Notion / Airtable / Google Sheets -> Create row | all `lead__*` fields |
| Optional | Filter by Zapier | continue only if `lead__priority` is `high`, for urgent alerts |

For Hebrew, `auto_reply__dir` is `rtl`. If right-to-left rendering matters, send the email as HTML and wrap the body in `<div dir="rtl">`.

## 5. Wire the site
Publish `src/form-hook.js` at the site root and add to the contact and owners pages in all six languages:
`<script src="/form-hook.js" data-endpoint="https://inonda-lead-intake.<account>.workers.dev" defer></script>`

## Checks after go-live
- Submit from the real site; confirm the Zap ran, the email arrived and the Slack/Notion entry exists.
- Post from a different origin (curl with another `origin` header); expect 403.
- Each lead uses one Zapier trigger plus one task per action.
