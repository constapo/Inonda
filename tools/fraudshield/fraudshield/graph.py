"""OCDS ingest + bidder/owner graph: find bidders that share directors, addresses
or phone numbers (common bid-rigging / shell-company indicator)."""
from collections import defaultdict
from . import Finding


def load_ocds(releases):
    """Flatten OCDS releases (list of dicts) into FraudShield tender records and party records."""
    tenders, parties = [], {}
    for r in releases:
        for p in r.get("parties", []):
            parties[p["id"]] = p
        t = r.get("tender", {})
        awards = r.get("awards", [])
        tenders.append({
            "id": r.get("ocid"),
            "buyer": (r.get("buyer") or {}).get("id") or (r.get("buyer") or {}).get("name"),
            "bids": [{"bidder": b.get("id"), "amount": (b.get("value") or {}).get("amount")}
                     for d in r.get("bids", {}).get("details", []) for b in [d]
                     ] if isinstance(r.get("bids"), dict) else [],
            "winner": (awards[0].get("suppliers") or [{}])[0].get("id") if awards else None,
            "award_value": (awards[0].get("value") or {}).get("amount") if awards else None,
            "bidders": [x.get("id") for x in t.get("tenderers", [])],
        })
    # drop bids lacking amount
    for t in tenders:
        t["bids"] = [b for b in t["bids"] if b.get("amount") is not None]
    return tenders, parties


def shared_attribute_links(parties, tenders):
    """Bidders in the same tender sharing address / phone / director name."""
    keys = defaultdict(set)
    for pid, p in parties.items():
        addr = (p.get("address") or {}).get("streetAddress", "").strip().lower()
        phone = (p.get("contactPoint") or {}).get("telephone", "").strip()
        if addr: keys[("address", addr)].add(pid)
        if phone: keys[("phone", phone)].add(pid)
        for d in p.get("directors", []):
            keys[("director", d.strip().lower())].add(pid)
    out = []
    for (kind, val), ids in keys.items():
        if len(ids) < 2:
            continue
        for t in tenders:
            both = ids & set(t.get("bidders", []))
            if len(both) >= 2:
                out.append(Finding("graph.shared_" + kind, "high",
                    f"Competing bidders share {kind}", {"tender": t["id"], "bidders": sorted(both), kind: val}))
    return out
