---
title: Deep Dive into LLMs like ChatGPT
date: 2025-06-11
description:  Or, how should we be thinking about LLMs?
tags:
  - ai
  - self-reflection
---

A couple of days back, I watched this 3.5 hour-long [video](https://www.youtube.com/watch?v=7xTGNNLPyMI&ab_channel=AndrejKarpathy) by Andrej Karpathy (ex-OpenAI founding member, ex-Tesla senior director of AI) titled "Deep Dive into LLMs like ChatGPT", and it provided some of the best insights about AI and **how we should be thinking about these models**.

I think the latter is underrated because it's possible to "know" how LLMs work but still not know how we should be thinking about them (e.g. the right mental models to have about them), so it's definitely super helpful to have one of the leading researchers in this field share his perspectives on this.

And since knowing the internals of the system makes you a better user of it, [this video](https://www.youtube.com/watch?v=7xTGNNLPyMI&ab_channel=AndrejKarpathy) will definitely make you more effective with AI tools.

Anyway, here are my notes from the video:

## Step 1: Pre-training

**"Download" and pre-process the internet**

(1) Gather an enormous quantity of high-quality text documents covering a wide range of topics.

(2) E.g. [FineWeb](https://huggingface.co/datasets/HuggingFaceFW/fineweb) dataset

**Tokenisation and Byte-Pair Encoding (BPE)**

(3) We don't train our models on raw text. Instead, we convert them into a 1-dimensional array of **tokens**. A token is just a small chunk of characters.

(4) BPE is the algorithm that creates these tokens from the huge dataset of gathered documents. It repeatedly merges the most frequent pairs of existing tokens (starts off as individual letters) into new tokens.

(5) This process builds a **vocabulary** of tokens — each token has a unique ID (a number) which represents it. The model works with these token IDs now, not the actual characters or text.

(6) E.g. the phrase "good morning" is broken down into 2 tokens — "good" and " morning", which have token IDs 30744 and 7709 respectively (for the tokeniser used by gpt-4o).

(7) A token need not be a full word. e.g. "fantastic" is broken down into 2 tokens: "fant" and "astic".

(8) You can play around with tokenisers [here](https://tiktokenizer.vercel.app/).

(9) But why do we tokenise? It's a trade-off between sequence length and vocabulary size. The longer the sequence of tokens we need to generate, the more computationally expensive it is. But we also want enough frequency of tokens so that training on them can uncover reliable statistical patterns that capture linguistic structure. ChatGPT uses a vocabulary of ~100k tokens

## Step 2: Base Model Training

(1) The goal of this step is to learn statistical patterns of language — i.e., which token is most likely to come next?

(2) We train a neural network on windows of tokens up to a maximum length (called the **context size**) and ask the model to predict the next token (token ID). In particular, the input is a list of at most context_size tokens to the model and the output is a probability distribution over all possible tokens (the vocabulary).

(3) Since we know the "true" next token from the training data (i.e., our data is labelled with the ground truth value automatically!), we can compute the loss and update the model's weights.

(4) At the end, we get a model which has learnt certain linguistic patterns and is very good at predicting the next token. Kind of like a "glorified autocomplete".

(5) But base models by themselves don't understand questions, answers, conversations, or tasks. They don't know that their job is to answer your questions. They will just use your prompt as a starting point and keep predicting the next token (until you tell them to stop). They are not "helpful assistants" yet. (So, almost all the LLMs you interact with online — ChatGPT, Claude, etc. — are more than just base models.)

(6) They are also prone to **regurgitation** (memorizing and repeating from training data) and **hallucination** (the model just taking its best guess in a probabilistic manner). This is because they're just sampling which token to output from some probability distribution which they have learnt during training. They don't know whether it's going to be factually correct or not. Remember: they are literally just predicting the next token.

(7) Yet, they can be made surprisingly capable with a technique called **few-shot prompting**. Basically, we can provide examples of how we'd like the model to behave in the prompt itself, and the model can "learn in context" without changing any of its weights. We don't really understand how it works, but it does improve response-quality a lot.

(8) E.g. Simply asking "What is 2 + 2?" might lead the AI to not even answer the question (it often goes on philosophical rants and continues by asking more such questions). But if the prompt is:"You are a helpful assistant.Human: What's the capital of France?AI: ParisHuman: What is 2 + 2?AI:"then empirically, the model answers the question (which is what we want) more often.

## Step 3: Post-training (Supervised Fine-Tuning)

(1) We want the model to be an assistant, not just a glorified autocomplete.

(2) So, we fine-tune the base model by training it on human-written conversations. This just means that we use the base model as the initial starting point, and use the same algorithm to train the model on this curated dataset of Q&A examples.

(3) In addition to the normal vocabulary, this step introduces special tokens whose purpose is to provide structure to the conversation — e.g. whose turn is it? when to stop responding? etc. OpenAI uses tokens such as <|im_start|> and <|im_end|> for this purpose.

(4) This curated dataset of conversations is crafted by expert labellers - their goal is not just to answer questions, but to demonstrate how an ideal assistant should behave.

(5) This improves the model from just predicting the next token based on all knowledge of the vast internet to trying to predict the ideal response by such an expert labeller[^1]. This is how we should be thinking about the difference between base models and SFT models.

(6) Of course, it doesn't completely forget all the knowledge it learnt in its pre-training phase too — the entire knowledge of the internet is condensed by the model into some hundreds of billions of weights (parameters).

(7) So, by training on this dataset of high-quality, human-crafted conversations, the model becomes skilled at imitating helpful, safe and informed behaviour.

## Interlude: Hallucinations and Tool Use

**Hallucinations**

(1) Why do LLMs hallucinate in the first place? Because all the conversations in the SFT stage include proper answers by human experts. They don't include answers like "i don't know" (because of how the dataset was constructed, by asking experts to write ideal responses in conversations). So, the model learns to imitate this by adopting a confident tone (just like an expert) and hallucinates when it doesn't know the answer.

(2) Even though the internals of the neural network (some subset of neurons) "know" that the model doesn't know the answer, it doesn't know how to say "i don't know" because it's never been encouraged to do so!

(3) Hence, the fix is pretty obvious: add more examples where the correct answer is "i don't know"! But how do we find questions to which the "correct" answer is "idk"? We can use another model to generate factual questions based on some text it finds online (LLMs are very good at this) and tests (they're also very good at this) whether this model gets it correct or wrong — you can ask the same question multiple times to make sure the AI is reliable / sure of it's answer or just guessing too. Then, explicitly add these questions with the answer "i don't know" in the dataset, and train the model on this updated conversations dataset.

(4) Basically, by showing the model that it's okay to answer "i don't know", the model learns to be less confident when it doesn't know the answer.

(5) By doing this, hallucination in models has drastically reduced.

**Tool Use**

(6) Instead of just mitigating hallucinations in cases where it doesn't know the answer, we can do better! When a human doesn't know something, we don't just say "i don't know" — we can also search the internet to find the answer. Why not let models do the same?

(7) The billions of weights of the model are just like a vague recollection of whatever the model has seen during its pre-training stage on the internet. It might remember some things correctly, get some things wrong, etc.

(8) But by allowing the model to search the web, you can refresh its memory with working memory to trigger those parts of the neural network that store that information that it had possibly learnt during pre-training. The context window is directly fed into the model as inputs, not as weights, so it's much more powerful in turning the knobs on the model's responses.

(9) Weights are like vague recollections, not always impactful on the output. Inputs are concrete, factual, and definitely taken into account while producing the output.

(10) But how can the LLM call tools and search the web? Well, the model is trained to generate tokens so the natural solution is to let it emit special tokens that ask the process running it to search the web for it[^2] (and pass the results to the model's context window, where it can use it directly when it resumes generating the output).

(11) E.g. the LLM can output <search_start>Who is the current President of USA?<search_end> to tell the process running it to search the web with this query if it doesn't have sufficient information to answer the question directly.

(12) How does the LLM learn that it can do this? Again, the way to train models to emit such special tokens (just as we did for conversations with <|im_start|> and <|im_end|>) is to include such conversations in the post-training dataset. For questions the model doesn't know the correct answer to, the ideal response (which is crafted by experts) would be to use search tools.

(13) As it trains on such conversations, it learns that when it doesn't know, it is encouraged to emit these search tokens, which then provide the relevant information directly inside the model's context window and help it generate the right answer[^3].

(14) We don't have to stop at search tools — the same idea can be used to allow the model to fetch data from some database, or from some documents, etc.

(15) Lesson: the way we're teaching these models is just by example.

(16) Takeaway: If you show examples of what you want to achieve in the context window (through few-shot prompting, or providing all the necessary information), the model is going to do a lot better than if you just expect it to retrieve it from the vague recollection from its pre-training phase (where it literally had to learn everything on the internet) aka its weights. Knowledge in the tokens of the context window is part of its working memory

## Models need tokens to think

(1) LLMs can only do a fixed amount of computation per token. A model is just a large mathematical expression that generates the next token. And there is a limit on how much computation this large mathematical expression can do.

(2) So, you cannot expect models to solve logic / math / reasoning problems in few tokens. It's fundamentally not possible.

(3) To solve hard problems, it helps to ask the model to think step-by-step such that each step is small enough that it can solve correctly. And by the end, it has all the necessary intermediate results in its context window that it can reach the final answer.

(4) So, for datasets involving reasoning models, the ideal expert answer should not just give the answer directly without any explanation (the model can't do so much computation in one token so its bound to fail at test-time!). We want the model to get into the "habit" of producing all the intermediate steps to arrive at the answer, because that's what turns out to be useful during inference. We want to distribute computation across many tokens and slowly arrive at the answer.

(5) This hypothesis can be proven empirically: if you ask the model to "answer in a single token" it gets many math / logic problems wrong vs. if you don't constrain the models with the number of tokens.

(6) Another way to get better answers for math / logic problems is to ask the model to write code. Models are very good at writing code but not very good at doing math computation. So, it can write code (emit special tokens for start of code and end of code) and then the process running the model can run this code and give the result back to the model (in its context window). Then, we don't have to rely on the model to do the calculations! It can just write the code, you can verify the steps yourself too, and let the python interpreter run the code and perform the actual arithmetic. Needless to say, code is far more reliable and deterministic for math than an LLM that predicts the next token.

(7) Similarly, models are bad at counting characters in a word — remember, they don't see words, they only see tokens (which might be chunks of a word)! And they're very bad with spelling as a result too. But they can copy-paste correctly and write code correctly. So, you can ask the model to "use code" for all these adversarial examples and it still gets it correct, because it relies on the code for the actual numeric operations / string manipulations, etc.

## Step 4: Reinforcement Learning Fine-Tuning

(1) Note: Not all models need to go through this step. Only "reasoning" models.

(2) Why do even need reinforcement learning if we already have supervised fine-tuning? Consider an analogy of students learning from a textbook:

   (a) Pre-training is like reading expository chapters — it gives general background knowledge, but no specific questions are solved.

   (b) Supervised Fine-Tuning (SFT) is like studying worked-out examples — you learn from expert solutions to problems.

   (c) Reinforcement Learning (RL) is like practicing with exercises where only the final answer is provided — you're forced to figure out how to get there on your own.

(3) This third stage is especially important for reasoning models, which must solve complex, multi-step problems in areas like math, logic, and science — not just provide factual answers.

(4) In SFT, the model learns to imitate expert demonstrations, but imitation only goes so far. RL allows the model to explore its own strategies to reach the correct answer.

(5) Humans don't always know the "best" way to explain or solve a problem from the model's perspective. What's simple for us may be inefficient for the model, and vice versa. So, for complex domains like reasoning and math, we often don't know how to annotate the data effectively. Instead, it's more powerful to let the model discover the most effective token sequences for solving problems.

(6) Basically, we're not in a good position to create these optimal token sequences for the LLM to learn problem-solving from because we don't know how big or small a single step should be / how best to break the problem down from a model's perspective. It's useful for models to learn to imitate experts as a means to initialise the system but at the end of the day, we really want the LLM to discover the token sequences that work best for itself. It needs to figure out what token sequences reliably get to the answer, given the prompt (because that's how they're going to be used by real users, not given the exact steps of reasoning to follow!). We're training them to think for themselves.

(7) How RL actually works? The model is given a question (prompt) and asked to generate many possible responses — often thousands. These outputs vary due to the model's stochastic nature. Some will be correct, some won't. Among these, we select the best answers (e.g., shortest correct answer), and add them to the training set. The model is now learning from its own generated data, rather than human annotations. More precisely, it's learning from it's best attempts at problem-solving (and internalising the patterns / problem-solving techniques that help it reach the correct answer).

(8) Okay, but if RL is so powerful, why bother with SFT at all? Because without SFT, the model would be completely lost at the start — like a student trying to solve problems with no idea what a solution even looks like. SFT bootstraps the model, placing it in the rough vicinity of correct solutions, so RL can then refine and personalise (figure out what works for itself) those strategies.

(9) Also, pre-training and SFT are well-established areas at this point. It is RL that is nascent and it's what enabled the latest boom in reasoning abilities of AI models.

(10) The output model after RL is not just imitating human experts. It can be coming up with completely novel ways of solving a problem, ones that it discovered for itself and thought would lead to the correct answer.

## Case study: DeepSeek R1

(1) Through RL, DeepSeek R1 learned to:

   (a) Try multiple ideas.

   (b) Evaluate which one might work.

   (c) Backtrack when stuck.

   (d) Try again — much like how humans approach tough problems.

(2) This exploratory behaviour was not explicitly taught or hardcoded — it's an **emergent property**. No one told the model to try different strategies; it _learned_ (during RL) that doing so improved its chances of getting the correct answer.

(3) This is why reasoning models often require more tokens: they are running complex internal simulations, juggling different strategies. What you see in DeepSeek's "thinking" section is the model's actual cognitive process, which is then distilled into a human-readable explanation. The model's thoughts can be messy — full of detours, false starts, and revisions. The final answer is cleaned up for presentation purposes (but all the "reasoning" is done in the "thinking" section). This strategy of explicitly working through reasoning steps is known as chain-of-thought prompting, and it naturally emerges from RL training.

(4) OpenAI doesn't show these full reasoning paths in its web UI — likely due to **distillation risk**. Other teams could scrape these outputs and train their own reasoning models by imitation.

(5) Even though reasoning models are so amazing for, well, reasoning tasks you don't need a reasoning model for factual queries (e.g., "When was Einstein born?") — a simpler, SFT-only model will suffice.

(6) If you only train on expert games, your model is limited to their strategies. You hit a ceiling. But RL lets models explore and discover new strategies, even ones no human has ever considered. AlphaGo demonstrated the full power of RL: it didn't just match expert Go players — it surpassed them. E.g. the infamous [move 37](https://www.youtube.com/watch?v=HT-UZkiOLv8).

(7) We're hoping that LLMs will eventually do the same — the equivalent of move 37 but in the broader, more general domain of problem-solving. Maybe it comes up with its own language that is easier to think in or whatever. In any case, we don't care how it arrives at the right answer (or in this case, a good solution) as long as it does. If it works, it works — even if we (mere mortals) can't comprehend why it should work.

## Finale: Reinforcement Learning with Human Feedback (RLHF)

(1) So far, we've focused on reinforcement learning in domains where answers are clearly right or wrong (e.g., math, logic). But what about writing a joke, or summarising a news article, or offering advice? In these cases, there's no definitive "correct" answer — so we can't just check if the model was right. And it's also very hard to give scores for these kinds of things. Most importantly, RL is extremely labour-intensive!

(2) Imagine you had to score every model output manually:

   1000 update steps × 1000 rollouts per prompt × 1000 prompts = 1 billion human judgments.

(3) This isn't scalable. So we use RLHF to drastically reduce the human labor.

(4) How RLHF Works:

   (a) Collect 5 model responses for each of 1000 prompts.

   (b) Ask humans to rank them from best to worst. (5000 human scores total — way more manageable.)

   (c) Train a "reward model" — a neural net that simulates human preferences.

   (d) Now run RL, but let the model optimise against the reward model instead of real humans.

(5) This (in my opinion brilliant!) trick using **indirection** replaces the costly human evaluation with a learned proxy[^4]. And RLHF also works great because:

   (a) Humans are better at ranking than giving precise scores. And we almost always don't need exact scores — just the relative order.

   (b) This lets us do RL in previously impossible domains, like writing, art, and conversation — areas where generation is hard, but ranking is easier. It's much harder to generate an "expert" or "ideal" joke, but much easier to compare 2 jokes and say which one is better. Andrej calls this the "discriminator-generator gap" because it's easier to discriminate between samples than actually generate the samples.

(6) But RLHF has a downside: the reward model is only a lossy approximation of human preferences. RL can discover ways to game this reward model — creating responses that fool it into assigning high scores, even if humans would find them nonsensical.

(7) For example: if the reward model learns that "the" appears more in good jokes, the model might eventually start generating jokes like:"the the the the the…"— which scores highly for the reward model, but not for people.

(8) These are called **adversarial examples**, and the more RL you run, the more the model might exploit such weaknesses in the reward model.

(9) So, in unverifiable domains, RLHF has a ceiling. Run it too long, and the model starts optimising for the proxy instead of real human preference. In verifiable domains (math, logic), this isn't a problem — there's a definitive correct answer which cannot be "fooled"!

[^1]: Of course it still does this generation token by token but now it's trying to imitate an expert human response to a question or in a conversation.

[^2]: This is such a beautiful and elegant design decision, I love it. When it comes to LLMs, "everything is a token": conversations, tools, etc.

[^3]: In particular, the model doesn't need to know what "search" is! It just has to emit that token ID — and we could've named that token anything, it doesn't matter. The model doesn't KNOW it's "searching the web". This is so cool!

[^4]: Which reminds me of a quote: "All problems in computer science can be solved with another level of indirection." by David Wheeler.
