import feedparser
import pathlib
import re
import os
import datetime
import httpx
import logging
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

root = pathlib.Path(__file__).parent.resolve()

def replace_chunk(content: str, marker: str, chunk: str, inline: bool = False) -> str:
    r = re.compile(
        r"<!\-\- {} starts \-\->.*<!\-\- {} ends \-\->".format(marker, marker),
        re.DOTALL,
    )
    if not inline:
        chunk = "\n{}\n".format(chunk)
    chunk = "<!-- {} starts -->{}<!-- {} ends -->".format(marker, chunk, marker)
    return r.sub(chunk, content)

def fetch_feed_entries(url: str, max_entries: int = 5) -> List[Dict[str, str]]:
    try:
        entries = feedparser.parse(url)["entries"]
        parsed_entries = []
        for entry in entries[:max_entries]:
            parsed_entry = {
                "title": entry.get("title", "No title"),
                "url": entry.get("link", "").split("#")[0],
                "published": entry.get("published", "").split("T")[0],
                "content": entry.get("description", ""),
                "description": entry.get("description", "")
            }
            parsed_entries.append(parsed_entry)
        return parsed_entries
    except Exception as e:
        logger.error(f"Error fetching feed from {url}: {str(e)}")
        return []

def fetch_photos_entries(url: str, max_entries: int = 1) -> List[Dict[str, str]]:
    try:
        entries = feedparser.parse(url)["entries"]
        return [
            {
                "title": entry.get("title", "No title"),
                "description": entry.get("description", ""),
                "photo": entry.get("media_content", [{}])[0].get("url", ""),
                "url": entry.get("link", "").split("#")[0],
                "published": entry.get("published", "").split("T")[0],
            }
            for entry in entries[:max_entries]
        ]
    except Exception as e:
        logger.error(f"Error fetching photos from {url}: {str(e)}")
        return []

def fetch_age() -> float:
    try:
        response = httpx.get(
            "https://us-central1-harperapi.cloudfunctions.net/age",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching age: {str(e)}")
        return 0.0

def read_file_content(file_path: pathlib.Path) -> str:
    try:
        return file_path.read_text()
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        return ""

def main():
    content = root / ".." / "content"
    readme = root / ".." / "README.md"

    file_paths = {
        "readme": readme,
        "bio": content / "bio.md",
        "links": content / "links.md",
        "details": content / "details.md",
        "github_stats": content / "github_stats.md",
        "social": content / "social.md",
    }

    # Read file contents concurrently
    with ThreadPoolExecutor() as executor:
        future_to_file = {executor.submit(read_file_content, path): name for name, path in file_paths.items()}
        file_contents = {name: future.result() for future, name in future_to_file.items()}

    rewritten = file_contents["readme"]
    original_content = rewritten  # Store the original content for comparison

    for section in ["bio", "links", "details", "github_stats", "social"]:
        rewritten = replace_chunk(rewritten, section, file_contents[section])

    # Fetch data concurrently
    with ThreadPoolExecutor() as executor:
        blog_future = executor.submit(fetch_feed_entries, "https://harper.blog/posts/index.xml")
        photos_future = executor.submit(fetch_photos_entries, "https://harper.photos/index.xml?")
        books_future = executor.submit(fetch_feed_entries, "https://reading.lol/index.xml")
        age_future = executor.submit(fetch_age)
        now_future = executor.submit(fetch_feed_entries, "https://harper.blog/now/index.xml", 1)

        blog_entries = blog_future.result()
        photos = photos_future.result()
        books = books_future.result()
        age = age_future.result()
        now_entries = now_future.result()

    entries_md = "\n".join(
        ["* [{title}]({url})".format(**entry) for entry in blog_entries]
    )
    rewritten = replace_chunk(rewritten, "blog", entries_md)

    photos_md = "\n".join(
        ["[![{title}]({photo})]({url}) \n *{description}*".format(**entry) for entry in photos]
    )
    rewritten = replace_chunk(rewritten, "photos", photos_md)

    books_md = "\n".join(
        ["* [{title}]({url})".format(**entry) for entry in books]
    )
    rewritten = replace_chunk(rewritten, "books", books_md)

    builddate_md = "Generated at `" + datetime.datetime.now().strftime("%c") + "`"
    rewritten = replace_chunk(rewritten, "date", builddate_md)

    age_md = f"- 👨Age: {age:.1f} years old"  # Display age with one decimal place
    rewritten = replace_chunk(rewritten, "age", age_md)

    # Handle the 'now' section
    if now_entries:
        now_md = f"""
{now_entries[0]['description']}
"""
    else:
        now_md = "No recent updates available. [Check here for the latest.](https://harperreed.com/now/)"

    rewritten = replace_chunk(rewritten, "now", now_md)

    # Only write to README.md if there are changes
    if rewritten != original_content:
        try:
            readme.write_text(rewritten)
            logger.info("README.md updated successfully")
        except Exception as e:
            logger.error(f"Error writing to README.md: {str(e)}")
    else:
        logger.info("No changes detected. README.md not updated.")

if __name__ == "__main__":
    main()
