# ABOUTME: Verify profile cards survive the scheduled README rebuild.
# ABOUTME: Check the published stats against the files produced by the metrics workflow.

import re
import unittest
from pathlib import Path

import yaml

from readme_builder.config import load_config
from readme_builder.main import build_readme
from readme_builder.renderers.readme import ReadmeAssembler

ROOT = Path(__file__).resolve().parents[1]


class ProfileMetricsTests(unittest.TestCase):
    def test_every_card_has_a_generator(self):
        stats = (ROOT / "content/github_stats.md").read_text()
        images = re.findall(r'<img\b[^>]*src="([^"]+)"[^>]*alt="([^"]+)"', stats)
        self.assertEqual(len(images), 7, "The profile should show all seven metrics cards")

        workflow = yaml.safe_load((ROOT / ".github/workflows/metrics.yml").read_text())
        cards = workflow["jobs"]["metrics"]["strategy"]["matrix"]["include"]
        self.assertEqual({src for src, _ in images}, {card["filename"] for card in cards})
        self.assertTrue(all(alt.strip() for _, alt in images))

    def test_readme_publishes_the_stats_source(self):
        config = load_config(ROOT / "config.yaml")
        assembler = ReadmeAssembler(config.readme_path, config.content_dir)
        stats = assembler.load_static_content("github_stats").strip()
        readme = assembler.load_readme()
        published = readme.split("<!-- github_stats starts -->")[1].split(
            "<!-- github_stats ends -->"
        )[0]
        self.assertEqual(published.strip(), stats)

    def test_rebuild_keeps_the_cards(self):
        config = load_config(ROOT / "config.yaml")
        stats = (config.content_dir / "github_stats.md").read_text().strip()
        rendered = build_readme(config, {})
        self.assertIn(stats, rendered)
        self.assertEqual(rendered.count("<!-- github_stats starts -->"), 1)
        self.assertEqual(rendered.count("<!-- github_stats ends -->"), 1)


if __name__ == "__main__":
    unittest.main()
