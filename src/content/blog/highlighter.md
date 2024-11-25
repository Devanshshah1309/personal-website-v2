---
title: I Built the World's First...
date: 2024-11-25
description: A tool that I now use daily.
tags:
  - building
---

I built the world’s first *correct* highlighter extension for chrome. Okay, I’m mostly exaggerating (but not really).

Check it out [here](https://chromewebstore.google.com/detail/minimal-highlighter/gioopdapheoejkiekebbkjjlnckhddde). It's completely free and doesn't require any sign-up.

Read on to find out about the story behind it.

---

I read a lot. On average, I spend ~ 1-2 hours / day reading long-form content on my laptop. This mostly includes books, blogs and newsletters.

And I’m a sucker for storing things I find interesting in one place so I can find it later on, because my memory isn’t super amazing (especially when someone asks “where did you find that?”, because I’m pretty decent with ideas and concepts, but bad with sources).

Until a few weeks ago, I was using Omnivore for reading articles and newsletters. It’s basically a free + open-source read-it-later app where you can store anything you want to read. It had a pretty sleek interface and a nice integration with Notion that helped me store my highlights there.

But they shut down, just as all free open-source projects eventually do. I tried Readwise, but I found it too overweight for my needs.
I just wanted a way to highlight things I was reading and copy them as markdown so I could easily paste it in Notion, with the formatting preserved (e.g. italics, bold text, headings, links, etc.).

So, I tried a bunch of chrome extensions but they all had a lot of functional bugs:

1. Does not highlight correctly when the text is formatted
2. The order of the highlights is that of the order in which you highlight, not the order in which the text appears on the page.
3. Overlapping highlights are not merged together — which means when copying, the overlapping part appears twice.
4. Adding multiple nested spans to the DOM for each overlapping highlight

Okay the last one’s not really functional (because the highlight is displayed the same to the user) but it’s annoying to see someone implement it the “wrong” way (yes, although such design decisions are mostly about trade-offs, there are still objectively better / worse implementations).

A typical example of a wrong implementation:

<video width="900" height="600" controls playsinline>
  <source src="https://imgur.com/ezRabg6.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

So, I decided to make my own. I thought it would take me like 2-3 hours max to build + publish. In the end, it took me ~20 hours (spread over a week) to get it right.

For example, when the selected text is across multiple paragraphs, you can’t just simply add a `<span class=”highlight”></span>` around the selected region because it will remove the paragraph break. So, you need to chop up the selected range into intervals, and then add spans for each of them.

But what if it partially overlaps with another highlight? How would you even detect that? And then how would you merge it? What if you need the highlight to be across other DOM nodes like `<strong>`, `<em>`, etc.? Do you still split the `<span>` each time?

There are a ton of edge cases here and I didn’t want to hard-code them (because I would probably have missed some of them), so I decided to use an algorithmic approach to this.

It’s similar to how you would solve the following problem: given a tree, with each node being a range (and ranges in a tree are sorted in increasing order of their endpoint), maintain the invariant that no 2 intervals overlap even as new intervals are added. And merge consecutive intervals whenever possible.

And so, what I did was:

1. Scan through existing highlights to detect overlaps
2. Add the interval to the DOM tree.
3. Run the  `merge` algorithm that checks siblings and descendants in order to merge adjacent / nested highlights.
4. When copying all highlights, detect all “enclosing” formatting tags and apply the markdown-equivalent of them.

And it works pretty nicely :)

<video width="900" height="600" controls playsinline>
    <source src="https://imgur.com/8mGfY8P.mp4" type="video/mp4">
    Your browser does not support the video tag.
</video>

You can find the chrome extension [here](https://chromewebstore.google.com/detail/minimal-highlighter/gioopdapheoejkiekebbkjjlnckhddde) — it would mean so much to me if you tried it out! (and lmk if there any other issues / features that would make you use this even more)
