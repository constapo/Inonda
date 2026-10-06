import argparse
import json
import sys
from dataclasses import asdict
from . import coordination, procurement, provenance, text


def _emit(findings):
    json.dump([asdict(f) for f in findings], sys.stdout, indent=2)
    print()
    return 1 if any(f.severity == "high" for f in findings) else 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="fraudshield")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("text"); s.add_argument("file")
    s = sub.add_parser("posts"); s.add_argument("json_file")
    s = sub.add_parser("tenders"); s.add_argument("json_file"); s.add_argument("--threshold", type=float)
    s = sub.add_parser("manifest"); s.add_argument("dir")
    s = sub.add_parser("verify"); s.add_argument("dir"); s.add_argument("manifest")
    a = ap.parse_args(argv)
    if a.cmd == "text":
        return _emit(text.analyze_text(open(a.file, encoding="utf-8").read()))
    if a.cmd == "posts":
        p = json.load(open(a.json_file))
        return _emit(coordination.near_duplicates(p) + coordination.bursts(p))
    if a.cmd == "tenders":
        return _emit(procurement.run_all(json.load(open(a.json_file)), a.threshold))
    if a.cmd == "manifest":
        print(provenance.dump(provenance.build_manifest(a.dir))); return 0
    if a.cmd == "verify":
        return _emit(provenance.verify(a.dir, json.load(open(a.manifest))))


if __name__ == "__main__":
    sys.exit(main())
