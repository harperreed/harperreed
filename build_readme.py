
import feedparser
import pathlib
import re
import os

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


if __name__ == "__main__":
    
    readme = root / "README.md"
    bio = root / "bio.md"
    links = root / "links.md"
    details = root / "details.md"

    readme_contents = readme.open().read()
    bio_contents = bio.open().read()
    link_contents = links.open().read()
    details_contents = details.open().read()



    rewritten = replace_chunk(readme_contents, "bio", bio_contents)
    rewritten = replace_chunk(rewritten, "links", link_contents)
    rewritten = replace_chunk(rewritten, "details", details_contents)

    ##rewritten = replace_chunk(rewritten, "bio", bio)



    entries = fetch_blog_entries()[:5]
    entries_md = "\n".join(
        ["* [{title}]({url})".format(**entry) for entry in entries]
    )
    rewritten = replace_chunk(rewritten, "blog", entries_md)


    photos = fetch_photos_entries()[:1]
    photos_md = "\n".join(
        ["![{title}]({photo})".format(**entry) for entry in photos]
    )
    rewritten = replace_chunk(rewritten, "photos", photos_md)

    books = fetch_books_entries()[:5]
    books_md = "\n".join(
        ["* [{title}]({url})".format(**entry) for entry in books]
    )
    rewritten = replace_chunk(rewritten, "books", books_md)    
    
    """
    rewritten = replace_chunk(rewritten, "blog", entries_md)
    """

    readme.open("w").write(rewritten)

