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
