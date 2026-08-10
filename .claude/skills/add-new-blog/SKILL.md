---
name: add-new-blog
description: Import a Substack post into this site as a new blog entry — writes the markdown file under src/content/blog/, downloads and converts its images, and chunks + embeds + uploads it to the Supabase vector DB used by the RAG chatbot. Use when the user gives a substack.com post URL and asks to add/import/publish it as a blog post on this site.
---

# Add a new blog post from Substack

Two independent phases. Phase A (write the `.md`) can be done and verified on
its own. Phase B (index to the vector DB) mutates a live production database
— always get explicit confirmation before running it, even if the user asked
for the whole thing in one go. Re-confirm per post if importing several.

Bundled helpers (run from the repo root):
- `.claude/skills/add-new-blog/scripts/html_to_md.py` — fetch + parse Substack HTML into markdown blocks/footnotes. Import it, don't reimplement it.
- `.claude/skills/add-new-blog/scripts/render_check.mjs` — render a markdown snippet through the site's actual remark/rehype pipeline, to catch parsing gotchas before they ship.

## Phase A — create the blog post

1. **Derive the slug** from the URL: the path segment after `/p/`, e.g.
   `https://X.substack.com/p/my-post-title` → slug `my-post-title`. This slug
   is used as the `.md` filename, the image folder name, and (later) the
   `blog_name` argument to the indexing script — keep it identical everywhere.

2. **Fetch the raw HTML** — do NOT use the `WebFetch` tool for this. It
   summarizes the page through a small model and silently mangles curly
   quotes, footnotes, and formatting. Fetch the byte-exact source instead:
   ```bash
   python3 .claude/skills/add-new-blog/scripts/html_to_md.py fetch "<substack_url>" /tmp/<slug>.html
   ```

3. **Pull metadata**:
   ```bash
   python3 .claude/skills/add-new-blog/scripts/html_to_md.py meta /tmp/<slug>.html
   ```
   Gives `title`, `date` (YYYY-MM-DD), `description`. The `description` is
   the post's own subtitle (the script already handles taking the *first*
   match — the page also contains the newsletter's generic bio further down,
   which is a decoy, do not use it).

4. **List images**:
   ```bash
   python3 .claude/skills/add-new-blog/scripts/html_to_md.py images /tmp/<slug>.html
   ```
   For each `src` URL: download it (`curl -sL -A "<same UA as in html_to_md.py>" <src> -o ...`),
   then **view the downloaded image** (Read tool) before naming it — the
   `scraped_alt` text is SEO junk from wherever the original author sourced
   the image (e.g. "Discover Andamanda Water Park near Phuket Town |
   Attractions near Amora Beach Resort Phuket"), not something to reuse as
   the markdown alt text. Write your own short, descriptive alt text based on
   what's actually in the image, matching the terse style of existing posts
   (check a few files in `src/content/blog/*.md` for tone).
   Convert every image to `.webp` (`cwebp -q 82 in.jpg -o out.webp` for
   photos, `-q 90` for diagrams/screenshots) and save into
   `public/images/blog/<slug>/<descriptive-name>.webp`.

5. **Convert the body to markdown** — write a short one-off Python snippet
   (don't hand-type the article text — it silently converts curly quotes/em
   dashes to straight ASCII and drifts from the source):
   ```python
   import sys; sys.path.insert(0, '.claude/skills/add-new-blog/scripts')
   from html_to_md import load_body, convert_body, get_footnotes

   soup, body = load_body('/tmp/<slug>.html')
   image_map = {
       'https://substack-post-media.s3.amazonaws.com/.../abc123_800x600.jpeg': ('Alt text', 'filename.webp'),
       # one entry per URL from step 4, in the exact original src form
   }
   body_md = convert_body(body, image_map, slug='<slug>')
   footnotes_md = get_footnotes(body)
   open('/tmp/<slug>_body.md', 'w').write(body_md + '\n\n' + footnotes_md + '\n')
   ```
   Read the result back and skim it before moving on.

6. **Write the frontmatter + assemble the file** at
   `src/content/blog/<slug>.md`. Match the schema in `src/content/config.ts`
   and the style of a recent post (e.g. `thoughts-on-using-ai-at-work.md`):
   ```yaml
   ---
   title: <sentence case, drop trailing period, keep proper nouns/acronyms capitalized>
   date: <YYYY-MM-DD from step 3>
   description: <verbatim from step 3>
   tags:
     - <reuse existing tags — grep `^  - ` across src/content/blog/*.md for the vocabulary; don't invent new ones>
   ---
   ```
   Then the body from step 5.

7. **Render-verify before calling it done** — this is not optional, it's how
   real bugs get caught (see Pitfalls). Start the dev server
   (`npm run dev`, or `vercel dev --listen 3000 --yes` if you need Supabase
   env vars wired in) and check `http://localhost:3000/posts/<slug>` returns
   200. No Playwright is installed in this repo — take screenshots with
   headless Chrome directly:
   ```bash
   "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
     --headless --disable-gpu --no-sandbox --window-size=1200,10000 \
     --screenshot=/tmp/<slug>.png "http://localhost:3000/posts/<slug>"
   ```
   The image will be taller than any single view — crop it into ~2000px
   bands with Pillow and Read each band, checking every image, footnote,
   list, code block, and blockquote actually rendered as intended (not as
   literal `_`/`*`/`<...>` — see pitfall below). Stop the server when done.

## Phase B — chunk + upload to the vector DB

Get explicit confirmation before this step. It writes to a live Supabase
Postgres instance shared with the production RAG chatbot.

**Key file:** `scripts/index_blogs.py`. **It does not take a CLI argument.**
The blog to process is a hardcoded string literal at the very bottom of the
file:
```python
if __name__ == "__main__":
    ...
    process_blogs('<some-previous-slug>')
```
To index a post: edit that line to the new slug, then run it from inside
`scripts/`:
```bash
cd scripts && python3 index_blogs.py
```
(`python3`, not the repo's `venv/` — see Pitfalls. Requires `COHERE_API_KEY`
and `DB_CONNECTION_STRING` in `.env`, already present in this repo.)

For **multiple new posts, run once per slug, sequentially** — edit the line,
run, verify, edit the line to the next slug, run, verify. Never leave the
argument as `''` (empty string processes *every* non-`DRAFT` post in the
folder and would re-embed/duplicate the whole site).

`process_blogs(blog_name)` matches `blog_name` as a **substring** against
every file's slug — before running, confirm your slug is unique so you don't
accidentally sweep in an unrelated post:
```bash
ls src/content/blog/*.md | xargs -n1 basename | sed 's/\.md$//' | grep -c "<slug>"
# must print exactly 1
```

**Verify after each run**, don't just trust a clean exit:
```bash
# 1. scripts/blog_records.json is overwritten each run — sanity check it
python3 -c "
import json
r = json.load(open('scripts/blog_records.json'))
print('records:', len(r), 'slugs:', set(x[0] for x in r))
"

# 2. confirm the rows actually landed in the DB
python3 -c "
import os, psycopg2
from dotenv import load_dotenv
load_dotenv('.env')
conn = psycopg2.connect(dsn=os.getenv('DB_CONNECTION_STRING'))
cur = conn.cursor()
cur.execute(\"SELECT count(*) FROM blog_chunks WHERE post_slug = %s\", ('<slug>',))
print(cur.fetchone())
"
```
Report the chunk count back to the user so they can spot-check the DB
themselves.

## Pitfalls (all previously hit for real — don't relitigate them)

1. **Never hand-type article text.** Always pull it out of the parsed HTML
   via `html_to_md.py`, so curly quotes (`’ “ ”`), em dashes, and ellipses
   match the source exactly instead of drifting to straight ASCII.

2. **Image alt text**: don't reuse Substack's scraped `alt` attribute — it's
   SEO text from the image's original source, not something the author
   wrote. Look at each image and describe it yourself.

3. **Adjacent bold/italic markdown delimiters break CommonMark parsing.**
   Substack's `<strong>A</strong><em><strong>B</strong></em><strong>C</strong>`
   naively converts to `**A**_**B**_**C**`, which Astro's remark/rehype
   pipeline mis-parses (leaks literal `_`/`**` into the rendered page instead
   of nesting bold+italic). Fix: put explicit word-boundary spacing between
   distinct delimiter runs and use `***text***` for combined bold+italic:
   `**A** ***B*** **C**`. **Always verify with `render_check.mjs`** rather
   than eyeballing the markdown — this is exactly the kind of bug that looks
   fine in the source and only shows up rendered.

4. **Literal `<tool_call>`-style text in prose is usually fine as plain
   text** (CommonMark's raw-HTML-tag grammar disallows underscores in tag
   names, so `<tool_call>` doesn't get parsed as a real tag and gets
   HTML-escaped automatically on output) — but don't assume, run it through
   `render_check.mjs` if it looks remotely tag-like.

5. **Image path convention**: use the relative form
   `../../../public/images/blog/<slug>/<file>.webp`, matching the most
   recent posts (e.g. `what-i-learnt-from-building-a-rag-chatbot.md`). Older
   posts (pre ~Aug 2025) use an absolute `/images/blog/...` form — don't
   copy that pattern for new posts.

6. **`scripts/index_blogs.py` has no dedupe/upsert.** Running it twice for
   the same slug inserts duplicate rows into `blog_chunks`. If you need to
   re-index a post, delete its existing rows first.

7. **The repo's `venv/` is broken** — it symlinks to a Homebrew Python 3.13.0
   Cellar path that no longer exists after a Homebrew upgrade. Use system
   `python3` for `index_blogs.py`; it already has `cohere`/`psycopg2`/
   `python-dotenv` available via user site-packages. (Worth fixing properly
   at some point — not blocking.)

8. **Substack renders footnote-content `<div>`s out of reading order** —
   they can appear after the "subscribe" CTA in the raw DOM even though they
   render inline at the bottom of the article. `get_footnotes()` handles
   this by reading `div.footnote` directly rather than relying on document
   position; don't try to inline footnote text while walking the body.

## Key files reference

| Path | Role |
|---|---|
| `src/content/blog/<slug>.md` | The blog post itself |
| `src/content/config.ts` | Frontmatter schema (title/date/description/tags/...) |
| `public/images/blog/<slug>/*.webp` | Post images |
| `scripts/index_blogs.py` | Chunks, embeds (Cohere), and inserts into `blog_chunks` |
| `scripts/blog_records.json` | Cache of the last run's (chunk, embedding) pairs — safety net if the DB insert fails, avoids re-embedding |
| `docs/indexing-blogs-for-rag.md` | Original short-form doc this skill automates |
| `.env` | `COHERE_API_KEY`, `DB_CONNECTION_STRING`, `SUPABASE_ANON_KEY`, `SUPABASE_PROJECT_URL` — already populated, don't need to create |
