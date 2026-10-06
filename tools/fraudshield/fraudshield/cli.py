import argparse
import json
import sys
from dataclasses import asdict
from . import calibrate, containment, coordination, graph, media, sanctions, procurement, provenance, text


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
    s = sub.add_parser("ocds"); s.add_argument("json_file"); s.add_argument("--threshold", type=float)
    s = sub.add_parser("media"); s.add_argument("file")
    s = sub.add_parser("trace"); s.add_argument("log"); s.add_argument("--geoip")
    s = sub.add_parser("quarantine"); s.add_argument("--admin-ip", required=True)
    s.add_argument("--apply", action="store_true"); s.add_argument("--i-own-this-host", action="store_true")
    s = sub.add_parser("sanctions-build"); s.add_argument("--db", default="data/sanctions.db"); s.add_argument("--csv")
    s = sub.add_parser("screen"); s.add_argument("names", nargs="+"); s.add_argument("--db", default="data/sanctions.db")
    a = ap.parse_args(argv)
    if a.cmd == "text":
        return _emit(text.analyze_text(open(a.file, encoding="utf-8").read()))
    if a.cmd == "posts":
        p = json.load(open(a.json_file))
        return _emit(coordination.near_duplicates(p) + coordination.bursts(p))
    if a.cmd == "tenders":
        return _emit(procurement.run_all(json.load(open(a.json_file)), a.threshold))
    if a.cmd == "ocds":
        t, parties = graph.load_ocds(json.load(open(a.json_file)))
        return _emit(procurement.run_all(t, a.threshold) + graph.shared_attribute_links(parties, t))
    if a.cmd == "media":
        return _emit(media.analyze_media(a.file))
    if a.cmd == "trace":
        rows = containment.trace(open(a.log), a.geoip)
        return _emit(containment.containment_findings(rows))
    if a.cmd == "quarantine":
        plan = containment.quarantine_plan(a.admin_ip)
        print("\n".join(plan))
        if a.apply:
            containment.apply_plan(plan, a.i_own_this_host); print("APPLIED")
        else:
            print("# dry run; add --apply --i-own-this-host as root to enforce")
        return 0
    if a.cmd == "sanctions-build":
        import os
        os.makedirs(os.path.dirname(a.db) or ".", exist_ok=True)
        path = a.csv or sanctions.download(os.path.join(os.path.dirname(a.db) or ".", "targets.simple.csv"))
        print(sanctions.build(path, a.db), "entities"); return 0
    if a.cmd == "screen":
        return _emit(sanctions.screen(a.db, a.names))
    if a.cmd == "manifest":
        print(provenance.dump(provenance.build_manifest(a.dir))); return 0
    if a.cmd == "verify":
        return _emit(provenance.verify(a.dir, json.load(open(a.manifest))))


if __name__ == "__main__":
    sys.exit(main())
