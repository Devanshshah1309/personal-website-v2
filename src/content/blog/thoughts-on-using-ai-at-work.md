---
title: Thoughts on using AI at work for the past 6 months
description: ''
date: 2026-05-05
tags:
  - ai
---

Background:

- graduated last year, studied computer science
- started working at a trading firm

### Claude-scrolling

One thing I’ve caught myself doing (when I’ve ~5-8 claude sessions running in parallel) is prioritising working on things that I know claude is good at, rather than what is more important.

It’s psychologically tempting to work on easy things that give you a quick dopamine hit when you complete it. So, making a quick script fix in 10 mins feels better than spending a few hours investigating why some part of our automation did not work as expected.

It’s tempting to spin up a quick dashboard / UI with nice and pretty charts (which you’re probably going to stop maintaining or caring about in a few days anyway) rather than deepdiving into why we missed a trade and how to capture such opportunities in the future.

Or improving your claude ←→ slack agentic workflow instead of spending time writing up the results of a backtest.

Been there, done that.

And the most dangerous part of this is that it feels like you’re doing “real work”. You’re constantly talking to claude and seeing it write tons of code. But truth be told, it’s still procrastination. Or at the very least, bad prioritisation.

If I’m honest: I still don’t think I can work on more than ~1-2 truly intellectually challenging “deep” tasks concurrently without an observable drop in productivity due to context-switching costs.

It took me a while to figure this out, and a slightly-longer while to admit this to myself. Why? Because multitasking feels cool and sexy, and it impresses people when you say you’re running 10 claude agents in parallel - of course they don’t ask what those 10 agents are actually doing and what impact it’s going to have.

### Building trust in claude

> I watched [Anthropic’s video on vibe coding in production](https://www.youtube.com/watch?v=fHWFF_pnqDk) and realised this was exactly what I was doing at work, and it gave me the right words to explain it.

One of the hardest things for me was to embrace the fact that I’m not going to be able to read all the code that AI writes. Because if I did, there wouldn’t be as big productivity gains.

But that doesn’t really solve the problem that everyone who has ever used an LLM faces: claude and its peers are often confidently wrong about things.

In my opinion, the way to build trust is to have some kind of testing / verification in place. BUT, critically, this doesn’t have to be at the code level - i.e., you still don’t have to read the code to convince yourself it’s correct. **You can simply use the code.**

Think of how typical QA teams (or product managers) at tech companies “verify” that your code meets the requirements without actually looking at your code.

Examples:

- If it’s a script, just run it on multiple test cases, edge cases, etc. and maybe even verify some invariants.
- If it’s a UI / frontend, you can just see that the layout and design looks good, play around with it to spot any performance issues, reload the page, etc.
- If it’s a full-stack product, you can still end-to-end test the functionality. Try performing some operations and observe the behaviour of the system. Does the database update correctly? Does the frontend use the new data? Is everything working as expected?

Too often, people don’t take enough time to play around with their own work before showing it to others, who then spot 13 bugs in 5 mins and get annoyed at the other person for using them as the bug-catcher instead of doing it themselves.

Admittedly, it’s much harder to verify some kind of outputs than others - e.g. it’s hard to verify that an analysis or a backtest that claude did is correct. And I face this issue a lot in my work. Specifically, I think it’s hard to build trust because when it comes to data, there are SO many different edge-cases to consider.

One thing that helps me a lot in these cases is using plan mode to get claude to interview me and ask me as many questions as it wants about the task at hand. And I can also give it all the edge cases for a particular task and how I think they should be handled. A small addition to all prompts that I’ve been using in plan mode is:

```
If you're not sure about anything, ask me. Never assume. Always ask. Ask me questions until you're at least 99% confident that you've understood the task and everything need to do.
```

I also ask claude to give me all the intermediate outputs that were generated in the process. Loosely speaking, for example, if I were using claude to backtest a strategy, it would have the following steps:

1. Data stored in database
2. Deriving features from this data
3. Backtesting the strategy

So, e.g. instead of just going from “prompt” → “looking at the final PnL graph of the backtest and the summary statistics” to decide whether a particular backtest result is good or bad, I inspect the intermediate outputs too, by asking it to create graphs and tables for those too. And I ask it to verify that certain invariants about the data hold true.

At each of these steps, I’m still actively making sure that it’s not doing anything obviously wrong. But all through graphs and tables and summaries and invariants - at a higher level of abstraction than code.

Why take all this extra effort? Why not just believe claude when it says “trust me bro” and call it a day? And then when someone else finds a flaw in it, why not just say “oops my claude made a mistake, i’ll get it to fix it'“?

Because if I’m going to submit / showcase anything, even if I used claude to do it, I personally want to stand behind it. I don’t want to sacrifice high quality standards just because I’m now going to delegate work to AI.

It’s embarassing for me personally if I keep submitting things that are blatantly wrong and people would (rightfully) stop trusting whatever I do. Not to mention that it’s bad for the company if people start taking “move fast and break things” too literally - because of the nature of the industry, the cost of breaking things in production typically outweighs the benefits of being deployed early and the marginal cost of spending some extra time to ensure correctness.

**You can delegate and outsource work but you can’t abdicate responsibility.**

So, a question that I often ask myself is: am I at least 95%+ confident in this work? (and to map this abstract concept of probability to an actual intuitive feeling: would i bet my $95 to someone else’s $5 that the work is correct?)

Of course different kinds of work require different thresholds of “correctness” but most of the work I do has a pretty direct impact on how we trade - which means the bar has to be incredibly high.

Keeping a bar of 100% is unreasonable because even software engineers make mistakes - bugs are inevitable but that doesn’t mean we throw our hands in the air and not do any kind of quality control / reviews for human-written code. Even if we cannot get to “zero bugs”, we can reduce them.

In the same way, I just try to add more checks and guardrails to verify the model’s work. That which cannot be eliminated may still be worth reducing!

### Being open-minded

Steve Jobs said something in his famous commencement speech that has stuck with me for many years:

> I didn't see it then, but it turned out that getting fired from Apple was the best thing that could've ever happened to me. **The heaviness of being successful was replaced by the lightness of being a beginner again, less sure about everything.** It freed me to enter one of the most creative periods of my life.

“Lightness of being a beginner again” is how I felt when I started using AI and how I feel right now too. I started from zero knowledge and it was a wonderfully joyful journey to learn about it by tinkering around, building random stuff with it, and just experimenting.

Even now, I’m learning new things about AI: the latest models, the latest cool features about harnesses (claude, codex, etc.), how the harnesses work underneath the hood, all about using multiple marketplaces and plugins seamlessly, etc.

But much more importantly, I’m learning how other people use AI. I’m learning their workflows, how they’ve come up with hacks and workarounds to fit their use-case. And I often just try out different people’s workflows to see if I like it or not.

I have my own ways of using claude too (e.g. tmux panels + badges for session names + alerts when it’s finished or blocked waiting for me to input + polling slack to spawn agents whenever i want to + … etc.) but I’m confident they’re far from optimal and I’m hill-climbing to improve them all the time. But to avoid getting stuck at a local optima, listening to how other people’s AI-workflows helps me random-restart into some other point in the how-to-use-ai landscape by giving me radically new ideas, and then I try to incrementally improve from there. Or combine the best of the two approaches into a better third alternative, like a genetic algorithm. (Okay, okay, I’ll stop with these search-algorithm analogies!)

And I think this is a good mindset to have for pretty much anything, but especially when things are changing so rapidly in a field like AI. Being too strongly opinionated about things which move so fast means you’re going to have to change your opinion quite often to actually incorporate all the latest information [^1]. e.g. are MCPs better than skills? should skills be comprehensive or should we just let the model figure things out? do models perform worse by getting confused when we give them too many tools?

Things that were true 2 weeks ago could be false now, and vice versa. Best practices are constantly evolving and we shouldn’t pretend as if we have all the answers. (Also it’s a lot more fun to just admit that you don’t know something and you’re figuring things out!)

In saying this, I would be super super keen to hear about your AI workflow and if you have any cool tips and tricks to share!

### Being a specialist even when using AI

As someone just starting out in their career, I want to build expertise in what I’m doing. I want to go deep and understand things better than what’s “just enough” to get the work done.

But using AI to do things typically makes learning harder - I’ve wrote about it way back in 2024. The tl;dr is that AI acts as an abstraction layer for you to go from “english” to “work done”, meaning you can do a LOT of work without knowing how it works underneath the hood at all.

This is fine for some things - it’s impossible to dig below every abstraction layer, and you shouldn’t have to - that’s the point of abstractions! [^2]

But if everyone just did this - used AI for all their work - no one would know how things worked underneath the hood. And no one would be able to debug when things broke and claude failed to fix it, or feel confident making a major change to the system.

At work, I’ve often thought that I’ve to be doing as much as I can in terms of maximising output and impact. But one thing my manager told me which changed the way I viewed things was:

> Learning compounds, impact is one-off. Don’t worry about having an impact right now. I want you to focus more on learning so that a year from now, or 2 years from now, you’ll be having much larger impact.

Essentially: take the time to build expertise and go deeper than you have to. As someone who is naturally curious, this should have been great news and also easy to put into practice. But it often conflicts with the part of me that feels like I need to be doing things which have an outcome instead of “just learning” - because learning is rarely visible and very hard to quantify. It’s like how reading books doesn’t feel like actual work even though you’re learning a lot.

I’m still working on feeling comfortable spending time at work “just learning”.

Now, when I do decide to go deep into some part of a codebase, I still use AI to help me. E.g. getting it to explain how different parts of the codebase interact with each other, how a specific parameter works, etc.

Once I think I’ve a good understanding of some specific topic, especially for ones that are not well-documented, I then write it up. I generally do this myself or give claude a long list of bullet points so it’s just paraphrasing what I’m saying into a more organized format. And then I ask a human expert in that domain to verify that my page is correct. It takes ~5 mins of their time + they’re happy that now there’s decent documentation for this + I’m happy because I’ve understood something well.

In my opinion [^3], the only things required to become an expert even when using AI to do work are: 1) being curious, 2) not being lazy.

[^1]: which is known to be difficult for us because we get attached to our beliefs too quickly and then require much more evidence to let go of them than we did to accept them in the first place

[^2]: this took me a while to accept and get used to — otherwise i would go down rabbit holes, tearing down every abstraction in my way, which was great fun but also very time-consuming.

[^3]: which has somewhat little experience backing it up
