# ABOUTME: Verify profile cards survive the scheduled README rebuild.
# ABOUTME: Check the published stats against the files produced by the metrics workflow.

import re
import shlex
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

from readme_builder.config import load_config
from readme_builder.main import build_readme
from readme_builder.renderers.readme import ReadmeAssembler

ROOT = Path(__file__).resolve().parents[1]


class ProfileMetricsTests(unittest.TestCase):
    def test_all_published_cards_are_valid_svgs(self):
        workflow = yaml.safe_load((ROOT / ".github/workflows/metrics.yml").read_text())
        cards = workflow["jobs"]["metrics"]["strategy"]["matrix"]["include"]
        for card in cards:
            with self.subTest(card=card["card"]):
                filename = ROOT / card["filename"]
                self.assertTrue(filename.is_file(), f"Missing generated card: {filename.name}")
                image = ET.parse(filename).getroot()
                self.assertEqual(image.tag, "{http://www.w3.org/2000/svg}svg")
                self.assertGreater(int(image.attrib["width"]), 0)
                self.assertGreater(int(image.attrib["height"]), 0)

    def test_repository_card_does_not_publish_false_zero_stars(self):
        image = ET.parse(ROOT / "metrics/repositories.svg").getroot()
        fields = image.findall('.//{http://www.w3.org/1999/xhtml}div[@class="field"]')
        text = " ".join(" ".join(field.itertext()) for field in fields)
        stars = re.search(r"(\d+)\s+Stargazers", text)
        self.assertIsNotNone(stars, "Repository card must include a star count")
        self.assertGreater(int(stars[1]), 0, "Harper's public repos have stars; reject empty data")

    def test_readme_bot_leaves_other_generated_files_unstaged(self):
        workflow = yaml.safe_load((ROOT / ".github/workflows/build.yml").read_text())
        commit_step = workflow["jobs"]["build"]["steps"][-1]["run"]
        stage = next(line for line in commit_step.splitlines() if line.startswith("git add "))

        with tempfile.TemporaryDirectory() as directory:

            def git(*arguments):
                return subprocess.run(
                    ["git", "-C", directory, *arguments],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()

            git("init")
            readme = Path(directory) / "README.md"
            cache = Path(directory) / "generated.pyc"
            readme.write_text("profile")
            cache.write_bytes(b"cache")
            git("add", "README.md", "generated.pyc")
            original_tree = git("write-tree")
            readme.write_text("profile with metrics")
            cache.write_bytes(b"updated cache")

            git(*shlex.split(stage)[1:])

            self.assertEqual(git("diff", "--cached", original_tree, "--name-only"), "README.md")

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
