import os, sys, tempfile, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from fraudshield import coordination, procurement, provenance, text


class T(unittest.TestCase):
    def test_near_duplicates(self):
        base = "this product changed my life and everyone should buy it right now today"
        posts = [{"id": i, "author": f"u{i}", "text": base + (" ok" if i % 2 else ""), "ts": 100 + i}
                 for i in range(6)]
        posts.append({"id": 99, "author": "z", "text": "completely unrelated remark about the weather", "ts": 5000})
        f = coordination.near_duplicates(posts)
        self.assertEqual(len(f), 1)
        self.assertEqual(len(f[0].evidence["authors"]), 6)
        self.assertTrue(coordination.bursts(posts))

    def test_procurement(self):
        tenders = [{"id": 1, "buyer": "B", "winner": "X", "award_value": 99000,
                    "bids": [{"amount": 5}, {"amount": 5}]}]
        names = {f.detector for f in procurement.run_all(tenders, threshold=100000)}
        self.assertIn("procurement.identical_bids", names)
        self.assertIn("procurement.threshold_splitting", names)

    def test_text_stock(self):
        t = ("As an AI language model, " + "the thing is good. " * 20)
        self.assertTrue(any(f.severity == "high" for f in text.analyze_text(t)))

    def test_provenance(self):
        with tempfile.TemporaryDirectory() as d:
            open(os.path.join(d, "a.txt"), "w").write("x")
            m = provenance.build_manifest(d)
            self.assertEqual(provenance.verify(d, m), [])
            open(os.path.join(d, "a.txt"), "w").write("y")
            self.assertEqual(provenance.verify(d, m)[0].detector, "provenance.modified")


if __name__ == "__main__":
    unittest.main()


class T2(unittest.TestCase):
    def test_graph(self):
        from fraudshield import graph
        rel = [{"ocid": "o1", "buyer": {"id": "B"},
                "parties": [{"id": "A", "address": {"streetAddress": "1 Main"}},
                            {"id": "C", "address": {"streetAddress": "1 MAIN"}}],
                "tender": {"tenderers": [{"id": "A"}, {"id": "C"}]}, "awards": []}]
        t, p = graph.load_ocds(rel)
        self.assertEqual(graph.shared_attribute_links(p, t)[0].detector, "graph.shared_address")

    def test_media(self):
        from fraudshield import media
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"\x89PNG....Midjourney job 123")
        self.assertEqual(media.analyze_media(f.name)[0].detector, "media.generator_metadata")

    def test_calibrate(self):
        from fraudshield import calibrate
        cases = [{"input": x, "label": x > 5} for x in range(10)]
        r = calibrate.sweep(lambda x, t: x > t, cases, {"t": [2, 5, 8]})
        self.assertEqual(r["params"]["t"], 5)

    def test_containment(self):
        from fraudshield import containment as c
        log = ['{"ts":1,"agent_id":"a","src_ip":"10.0.0.2","cmd":"ls"}',
               '{"ts":9,"agent_id":"a","src_ip":"8.8.8.8","cmd":"curl x"}']
        rows = c.trace(log)
        self.assertEqual(rows[0]["src_ip"], "8.8.8.8"); self.assertEqual(rows[0]["ip_class"], "public")
        with self.assertRaises(ValueError): c.quarantine_plan("1.2.3.4; rm -rf /")
        with self.assertRaises(PermissionError): c.apply_plan(c.quarantine_plan("10.0.0.5"), False)
