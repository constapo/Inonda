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
