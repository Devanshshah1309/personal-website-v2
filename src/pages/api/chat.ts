import process from 'node:process'
import { createClient } from '@supabase/supabase-js'
import { CohereClient } from 'cohere-ai'
import type { APIRoute } from 'astro'

interface BlogChunk {
  url_path: string
  content_txt: string
}

// Initialize Cohere
const cohere = new CohereClient({
  token: process.env.COHERE_API_KEY!,
})

// Initialize Supabase client
const supabase = createClient(
  process.env.SUPABASE_PROJECT_URL!,
  process.env.SUPABASE_ANON_KEY!,
  {
    auth: {
      persistSession: false,
    },
  },
)

export const POST: APIRoute = async ({ request }) => {
  if (!request.body) {
    console.error('Function error: Request body is missing.')
    return new Response(JSON.stringify({ error: 'Request body is missing.' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    })
  }

  let query
  try {
    const data = await request.json()
    query = data.query
  }
  catch (e: any) {
    console.error('Function error: Invalid JSON in request body.', e)
    return new Response(JSON.stringify({ error: 'Invalid JSON in request body.' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    })
  }

  if (!query || typeof query !== 'string') {
    console.error('Function error: Missing or invalid query parameter.')
    return new Response(JSON.stringify({ error: 'Missing or invalid query parameter.' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    })
  }

  try {
    // Get embedding for the query
    const embedRes = await cohere.embed({
      model: 'embed-english-v3.0',
      texts: [query],
      inputType: 'search_query',
    })
    const queryVector = (embedRes.embeddings as number[][])[0]

    // Search for relevant content
    const { data: matches, error } = await supabase
      .rpc('match_blog_chunks', {
        query_embedding: queryVector,
        match_threshold: 0.8,
        match_count: 10,
      })

    if (error)
      throw error
    if (!matches?.length) {
      return new Response(JSON.stringify({ answer: 'I don\'t have information about that yet.' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    }

    // Build context from matches
    const contextText = (matches as BlogChunk[])
      .map((m, idx) => (`${idx + 1}) [${m.url_path}] "${m.content_txt.trim()}"`))
      .join('\n\n')

    const epilog = `\nDon't ask me if I would like to know anything more. Don't repeat anything unnecessarily. Be specific and concise. Quote specific sentences from the context wherever applicable. Keep your response to less than 100 words.`

    // Generate response
    const chatRes = await cohere.chat({
      model: 'command',
      message: query + epilog,

      preamble: `You are a knowledgeable blogger. Answer the question based ONLY on the following context provided, which are snippets of blogs written by you. Rules to follow:
- Be confident, courteous and concise in your tone.
- Cite the exact name of the blog you're quoting from wherever possible
- Answer in first-person, not third-person.
- Always keep your response less than 100 words.
- Quote specific sentences from the documents provided wherever applicable.
- Never ask the user if they would like to know more. Never end your response with a question.
- Never end with "let me know if you want me to elaborate".
- If you cannot answer the question based on the context provided, say "I don't know".
- Your reply should only consists of alphabets, numbers and puncuations. Never include any html tags or markdown symbols.

Context:
    ${contextText}}`,
      temperature: 0.1,
      maxTokens: 180,
    })

    return new Response(JSON.stringify({
      answer: chatRes.text,
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    })
  }
  catch (err: any) {
    console.error('Function error:', {
      message: err.message,
      stack: err.stack,
      env: {
        hasCohereKey: !!process.env.COHERE_API_KEY,
        hasDbString: !!process.env.DB_CONNECTION_STRING,
        hasSupabaseKey: !!process.env.SUPABASE_ANON_KEY,
      },
    })
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    })
  }
}
