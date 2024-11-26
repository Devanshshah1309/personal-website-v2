---
title: I Built the World's First Correct Highlighter...
date: 2024-11-25
description: Or so I thought...
tags:
  - building
---

I built the world’s first *correct* highlighter extension for chrome. Okay, I’m mostly exaggerating.

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

Or so I thought...

I quickly realized that even my highlighter was far from perfect, and was facing multiple issues. Just not the issues other extensions were facing.

It was a more fundamental issue: in many cases, I didn't know what the ideal output should even look like. And it's, um, quite hard to build something if you don't even know what it's supposed to do.

For example,

1. If you highlight 2 separate sentences in the same paragraph, and then copy them, should they be put in the same paragraph? Or should there be aline break between them?
2. When you highlight a part of the sentence that is in an unordered list, should the markdown output have the list format? If yes, what if you highlight two disjoint parts of the same list item? Should they be in the same list item, or should there be two list items?
3. If you have a nested list, but you only highlight an inner list item, should the markdown output have the nested list structure or just a single layer list?

I decided to step back and reevaluate what I was doing.

I realized that I had set out to build "the" correct highlighter, but in the process, learnt that there is probably no such thing, because everyone's expectations of what the output should look like are different.

In fact, even for my own use-case, I realized that I wanted different kinds of markdown outputs at different times. For example, sometimes, I want all the highlights to be prefixed with a `>` so that they become quotes, and sometimes, I want them to have the original formatting (as on the page).

So, nope, in the end, I did not actually build the world's first correct highlighter, and in fact, it'll probably never exist.

Lesson: Building the "correct" XYZ is a strong claim. It's much better to try to build a *better* XYZ where the definition of "better" is independent of the user (or at least, *many* people can collectively agree on what "better" is). There's rarely any one-size-fits-all solution when it comes to software, from browsers to note-taking apps (which is why you see so many similar products in the market - they cater to different groups of users).

(Also, I don't think many people would care about the 1% edge cases anyway -- they would much rather have an easy-to-use tool with a good UI that works *almost* always. And so, it would've failed the "make something people want" test.)

Somehow, I feel I'm satisfied with this conclusion, yet I'm glad I built this anyway.

You can find it [here](https://chromewebstore.google.com/detail/minimal-highlighter/gioopdapheoejkiekebbkjjlnckhddde), if you're still interested!
