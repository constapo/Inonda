# FraudShield (prototype)

Stdlib-only Python. Run tests: `python3 -m unittest discover -s tests`

```
python3 -m fraudshield.cli text doc.txt
python3 -m fraudshield.cli posts posts.json          # [{id,author,text,ts}]
python3 -m fraudshield.cli tenders tenders.json --threshold 100000
python3 -m fraudshield.cli manifest ./docs > manifest.json
python3 -m fraudshield.cli verify ./docs manifest.json
```
Exit code 1 if any high-severity finding. See DESIGN.md.

## v1 additions
```
python3 -m fraudshield.cli ocds releases.json         # OCDS feed + shared director/address/phone graph
python3 -m fraudshield.cli media photo.png            # C2PA presence/validation (needs c2patool), AI-generator metadata, pluggable classifiers
python3 -m fraudshield.cli trace agent.log [--geoip db.csv]   # last command + source IP per AI agent (JSONL: ts,agent_id,src_ip,cmd)
python3 -m fraudshield.cli quarantine --admin-ip 10.0.0.5     # DRY RUN nftables isolation plan
python3 -m fraudshield.cli quarantine --admin-ip 10.0.0.5 --apply --i-own-this-host   # root only
```
`fraudshield.calibrate.sweep` tunes detector thresholds on labelled cases (max recall at a precision floor).

### Containment scope and limits
- Works only on hosts you administer; it never connects to remote systems or retaliates.
- Quarantine drops all traffic except loopback and one admin IP (SSH). It cannot "close all ports on any system", only the machine it runs on.
- A source IP is where a command arrived from, often a VPN/proxy/Tor exit or compromised relay; geolocation (offline CSV you supply) is approximate and is a lead for your provider/law enforcement, not proof of identity.

## Sanctions database (OpenSanctions)
```
python3 -m fraudshield.cli sanctions-build        # downloads targets.simple.csv into data/ and builds data/sanctions.db
python3 -m fraudshield.cli screen "Some Company Ltd" "Jane Doe"
```
Data is CC BY-NC 4.0 (commercial use needs a licence) and is git-ignored. Name matching is exact on normalized tokens, so hits need human review and misses are possible. Needs network access to data.opensanctions.org.
