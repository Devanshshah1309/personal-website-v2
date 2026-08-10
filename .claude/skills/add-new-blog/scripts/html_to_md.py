#!/usr/bin/env python3
"""
Helpers for converting a saved Substack post's raw HTML into this site's
blog markdown format. See ../SKILL.md for the full recipe this supports.

CLI usage:
    python3 html_to_md.py fetch <substack_url> <out.html>
    python3 html_to_md.py meta <out.html>
    python3 html_to_md.py images <out.html>

Library usage (for the actual markdown assembly — see SKILL.md step 3):
    from html_to_md import load_body, convert_body, get_footnotes
    soup, body = load_body("out.html")
    image_map = {
        "https://substack-post-media.../abc123_800x600.jpeg": ("Alt text here", "my-filename.webp"),
        ...
    }
    body_md = convert_body(body, image_map, slug="my-post-slug")
    footnotes_md = get_footnotes(body)
"""
import json
import re
import subprocess
import sys

from bs4 import BeautifulSoup, NavigableString

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def fetch(url, out_path):
    """Fetch raw Substack HTML with curl. Do NOT use WebFetch for this —
    it summarizes through a small model and silently mangles quotes/
    footnotes/formatting. We need the byte-exact source."""
    subprocess.run(["curl", "-sL", "-A", UA, url, "-o", out_path], check=True)


def load_body(html_path):
    html = open(html_path, encoding="utf-8").read()
    soup = BeautifulSoup(html, "html.parser")
    body = soup.find("div", class_="body markup")
    if body is None:
        raise RuntimeError(
            "Could not find div.body.markup — Substack's page structure may "
            "have changed since this script was written."
        )
    return soup, body


def extract_meta(html_path):
    """Pull title/date/description out of the page's inline JSON-LD-ish blob.

    NOTE: "description" appears at least twice in the page — the FIRST match
    is the post's own subtitle (what we want), later matches are the
    newsletter's generic bio. Only use the first.
    """
    html = open(html_path, encoding="utf-8").read()

    def grab_first(key):
        m = re.search(r'"%s":"((?:[^"\\]|\\.)*)"' % key, html)
        return m.group(1) if m else None

    date_published = grab_first("datePublished") or ""
    return {
        "title": grab_first("headline"),
        "date": date_published[:10],  # YYYY-MM-DD
        "description": grab_first("description"),
    }


def list_images(body):
    """Return [(original_src_url, scraped_alt, caption), ...] in document
    order for every real content image (figures the author placed inline).
    The scraped alt text is usually SEO junk from wherever the author found
    the image (e.g. "Discover Andamanda Water Park near Phuket Town |
    Attractions near...") — do not reuse it verbatim, see SKILL.md pitfalls.
    """
    out = []
    for cic in body.find_all("div", class_="captioned-image-container"):
        img = cic.find("img")
        fc = cic.find("figcaption")
        d = json.loads(img.get("data-attrs") or "{}")
        out.append((d.get("src"), img.get("alt"), fc.get_text() if fc else None))
    return out


def inline_to_md(el):
    """Convert inline content (text + em/strong/s/code/a/br/span) to markdown."""
    out = []
    for c in el.children:
        if isinstance(c, NavigableString):
            out.append(str(c))
        elif c.name == "em":
            out.append("_" + inline_to_md(c) + "_")
        elif c.name == "strong":
            out.append("**" + inline_to_md(c) + "**")
        elif c.name == "s":
            out.append("~~" + inline_to_md(c) + "~~")
        elif c.name == "code":
            out.append("`" + c.get_text() + "`")
        elif c.name == "a":
            if "footnote-anchor" in (c.get("class") or []):
                fid = c.get("href", "").replace("#footnote-", "")
                out.append(f"[^{fid}]")
            else:
                out.append("[" + inline_to_md(c) + "](" + c.get("href", "") + ")")
        elif c.name == "br":
            out.append("\n")
        else:
            out.append(inline_to_md(c))
    return "".join(out)


def list_to_md(el, ordered, depth=0):
    """Convert a ul/ol to markdown, recursing into nested ul/ol (Substack
    renders pseudocode-style indented lists this way)."""
    lines = []
    idx = 1
    indent = "   " * depth  # 3 spaces = width of "1. " marker, required for CommonMark nesting
    for li in el.find_all("li", recursive=False):
        parts = []
        sub_lists_md = []
        for c in li.find_all(["p", "ul", "ol"], recursive=False):
            if c.name == "p":
                parts.append(inline_to_md(c))
            else:
                sub_lists_md.append(list_to_md(c, c.name == "ol", depth + 1))
        text = " ".join(parts).strip()
        bullet = f"{idx}." if ordered else "-"
        lines.append(f"{indent}{bullet} {text}")
        lines.extend(sub_lists_md)
        idx += 1
    return "\n".join(lines)


def convert_body(body, image_map, slug):
    """Walk the top-level children of div.body.markup and produce the post
    body as markdown (everything except the frontmatter and footnotes).

    image_map: {original_src_url: (alt_text, filename.webp)}, where
    filename.webp is just the basename inside
    public/images/blog/<slug>/ — this function builds the full relative
    ../../../public/images/blog/<slug>/<filename> path used by this site.
    """
    blocks = []
    for el in body.find_all(recursive=False):
        if el.name == "p":
            txt = inline_to_md(el).strip()
            if txt:
                blocks.append(txt)
        elif el.name in ("ul", "ol"):
            blocks.append(list_to_md(el, el.name == "ol"))
        elif el.name == "h3":
            blocks.append("### " + inline_to_md(el).strip())
        elif el.name == "blockquote":
            qtext = inline_to_md(el).strip()
            qlines = qtext.split("\n")
            blocks.append("\n".join("> " + l if l.strip() else ">" for l in qlines))
        elif el.name == "div":
            cls = el.get("class") or []
            if "captioned-image-container" in cls:
                img = el.find("img")
                d = json.loads(img.get("data-attrs") or "{}")
                src = d.get("src")
                if src not in image_map:
                    raise KeyError(
                        f"No entry in image_map for {src!r}. Download every "
                        "image from list_images() and add it before converting."
                    )
                alt, fname = image_map[src]
                image_line = f"![{alt}](../../../public/images/blog/{slug}/{fname})"
                # If Substack has a figcaption, this site's convention (see
                # e.g. joy-and-productivity.md) is a plain-text line directly
                # under the image, NO blank line in between — so caption text
                # must be appended to the SAME block, not a separate one.
                fc = el.find("figcaption")
                if fc is not None and fc.get_text().strip():
                    image_line += "\n" + inline_to_md(fc).strip()
                blocks.append(image_line)
            elif "footnote" in cls:
                pass  # handled by get_footnotes()
            elif "subscription-widget-wrap" in cls:
                pass  # Substack's own subscribe CTA — not real content
            elif "pencraft" in cls and el.find("pre"):
                code = el.find("code").get_text()
                blocks.append("```\n" + code + "\n```")
            # anything else inside body markup is share buttons / UI chrome — skip
    return "\n\n".join(blocks)


def get_footnotes(body):
    """Return the [^n]: ... footnote block as a single markdown string,
    already sorted numerically and blank-line separated."""
    fn = {}
    for el in body.find_all("div", class_="footnote", recursive=False):
        fid = el.find("a", class_="footnote-number").get("id").replace("footnote-", "")
        content_div = el.find("div", class_="footnote-content")
        paras = [inline_to_md(p).strip() for p in content_div.find_all("p", recursive=False)]
        fn[fid] = "\n\n".join(paras)
    return "\n\n".join(f"[^{k}]: {v}" for k, v in sorted(fn.items(), key=lambda x: int(x[0])))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "fetch":
        fetch(sys.argv[2], sys.argv[3])
        print(f"saved to {sys.argv[3]}")
    elif cmd == "meta":
        print(json.dumps(extract_meta(sys.argv[2]), indent=2))
    elif cmd == "images":
        _, body = load_body(sys.argv[2])
        for src, alt, caption in list_images(body):
            print(json.dumps({"src": src, "scraped_alt": alt, "caption": caption}))
    else:
        print(f"unknown command: {cmd}")
        sys.exit(1)
