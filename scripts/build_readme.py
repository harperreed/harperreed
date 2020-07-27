
import feedparser
import pathlib
import re
import os
import datetime
import httpx

root = pathlib.Path(__file__).parent.resolve()

def replace_chunk(content, marker, chunk, inline=False):

    r = re.compile(
        r"<!\-\- {} starts \-\->.*<!\-\- {} ends \-\->".format(marker, marker),
        re.DOTALL,
    )
    if not inline:
        chunk = "\n{}\n".format(chunk)
    chunk = "<!-- {} starts -->{}<!-- {} ends -->".format(marker, chunk, marker)
    return r.sub(chunk, content)

def fetch_books_entries():
    entries = feedparser.parse("https://reading.lol/index.xml")["entries"]
    return [
        {
            "title": entry["title"],
            "url": entry["link"].split("#")[0],
            "published": entry["published"].split("T")[0],
        }
        for entry in entries
    ]


def fetch_photos_entries():
    entries = feedparser.parse("https://harper.photos/index.xml?")["entries"] 
    return [
        {
            "title": entry["title"],
            "description": entry["description"],
            "photo": entry["media_content"][0]["url"],
            "url": entry["link"].split("#")[0],
            "published": entry["published"].split("T")[0],
        }
        for entry in entries
    ]
    

def fetch_blog_entries():
    
    entries = feedparser.parse("https://harper.blog/index.xml")["entries"]
    return [
        {
            "title": entry["title"],
            "url": entry["link"].split("#")[0],
            "published": entry["published"].split("T")[0],
        }
        for entry in entries
    ]

def fetch_age():
    
    return httpx.get(
        "https://us-central1-harperapi.cloudfunctions.net/age",
    ).json()

if __name__ == "__main__":
    content = root / ".."  / "content"
    
    readme = root / ".."  / "README.md"

    bio = content / "bio.md"
    links = content / "links.md"
    details = content / "details.md"
    github_stats = content / "github_stats.md"
    social = content / "social.md"

    readme_contents = readme.open().read()
    bio_contents = bio.open().read()
    link_contents = links.open().read()
    details_contents = details.open().read()
    github_stats_contents = github_stats.open().read()
    social_contents = social.open().read()


    rewritten = replace_chunk(readme_contents, "bio", bio_contents)
    rewritten = replace_chunk(rewritten, "links", link_contents)
    rewritten = replace_chunk(rewritten, "details", details_contents)
    rewritten = replace_chunk(rewritten, "github_stats", github_stats_contents)
    rewritten = replace_chunk(rewritten, "social", social_contents)

    entries = fetch_blog_entries()[:5]
    entries_md = "\n".join(
        ["* [{title}]({url})".format(**entry) for entry in entries]
    )
    rewritten = replace_chunk(rewritten, "blog", entries_md)


    photos = fetch_photos_entries()[:1]
    photos_md = "\n".join(
        ["[![{title}]({photo})]({url}) \n *{description}*".format(**entry) for entry in photos]
    )
    rewritten = replace_chunk(rewritten, "photos", photos_md)

    books = fetch_books_entries()[:5]
    books_md = "\n".join(
        ["* [{title}]({url})".format(**entry) for entry in books]
    )
    rewritten = replace_chunk(rewritten, "books", books_md)    

    builddate_md = "Generated at `" + datetime.datetime.now().strftime("%c") + "`"
    rewritten = replace_chunk(rewritten, "date", builddate_md)

    age_md ="- 👨Age: " + str(fetch_age()) + " years old"

    rewritten = replace_chunk(rewritten, "age", age_md)
    print(rewritten)
    readme.open("w").write(rewritten)


