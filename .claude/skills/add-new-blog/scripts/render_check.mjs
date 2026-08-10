// Renders a markdown snippet through the SAME remark/rehype pipeline Astro
// uses, so you can verify a tricky bit of markdown (nested bold/italic,
// literal "<tag>"-looking text, etc.) actually produces the HTML you expect
// BEFORE trusting it in a blog post. See SKILL.md pitfall #3.
//
// Must be run with cwd = the repo root (so it resolves unified/remark/etc.
// from node_modules) via: node .claude/skills/add-new-blog/scripts/render_check.mjs <file.md>
import fs from 'node:fs'
import process from 'node:process'
import { unified } from 'unified'
import remarkParse from 'remark-parse'
import remarkRehype from 'remark-rehype'
import rehypeStringify from 'rehype-stringify'
import remarkGfm from 'remark-gfm'

const path = process.argv[2]
if (!path) {
  console.error('usage: node render_check.mjs <snippet.md>')
  process.exit(1)
}
const md = fs.readFileSync(path, 'utf8')

unified()
  .use(remarkParse)
  .use(remarkGfm)
  .use(remarkRehype, { allowDangerousHtml: true })
  .use(rehypeStringify, { allowDangerousHtml: true })
  .process(md)
  .then(file => process.stdout.write(`${String(file)}\n`))
  .catch((e) => {
    console.error('ERR', e)
    process.exit(1)
  })
