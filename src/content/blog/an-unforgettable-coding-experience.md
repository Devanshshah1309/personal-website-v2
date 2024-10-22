---
title: An Unforgettable Coding Experience
date: 2023-05-11
description: How I learnt to despise the big bang.
tags:
    - anecdote
    - swe
---

## Story Time: An Unforgettable Coding Experience

This is not an essay; it's an impulsive writing, a raw anecdote (+ some key software engineering lessons). If you’re expecting something well-researched or a “well-written” (whatever that might mean) article, i don’t want to disappoint you - so stop reading. If you’re looking for a good story with lots to learn from, continue reading! 😄

I attended the Code to Connect 2023 competition conducted by Bank of America at their Singapore office today (May 11, 2023), and this was an unforgettable coding experience.

Don’t get me wrong here - I mean unforgettable in a very “not-so-good” fashion - you’ll understand soon enough.

I reached the office at 7:30am (yes, I woke up at 5am just for this - totally worth it though) and met my teammates - we got along pretty well. After the problem statement was explained to us, we started coding at around 9am. It might be good to mention here that the deadline ƒor submitting the code was 5:00pm. So we had about 8 hours to implement a \<redacted due to non-disclosure agreement\> - basically, something related to equity trading.

This is when it all begins. We spent about 20 minutes deciding the overall software architecture before diving straight into coding - all seems to be going well, and we’re making good progress. 3 hours in. We’re nearly done with all the components - all that’s left to do is integrate everything and test that it works.

After lunch, we continued - everyone was in a good mood, comfortable and quite relaxed. And then, everything with southward.

We realised we had a major problem - we hadn’t really thought carefully enough about how the different components would be interacting with each other. We thought we’d develop that communication interface “as we go along”. As it turns out, there was a circular import dependency (not in our logic, but in our codebase). For context, we were using python and had separated each component as a class in a different file.

There didn’t seem to be any easy way to fix this. Some of the mentors from Bank of America very kindly explained to us the problem and together, we all started discussing possible alternative implementation ideas - all of which were either super hacky - e.g. putting all the components into a single file - (believe me, seeing solutions would make me cry) or required major refactoring (for which we didn’t have time).

Also, on closer inspection we kept uncovering more and more bugs - simply because we had forgotten to account for these things beforehand. For example, our entire codebase was running sequentially (instead of asynchronously, as was required by the specifications) and there was no way we could make it multi-threaded given the current implementation.

For about 20 minutes, I didn’t speak a word - probably a mixture of guilt, embarrassment (for not thinking of such obvious problems) and panic (yeah, mostly this tbh). Then, after sufficient mourning, we decided to re-architect the entire codebase nearly from scratch - we clearly defined our APIs, our logic, everything.

We spent about 45 minutes doing this - on paper! During this time, we didn’t write a single line of code, but this was, without a doubt, the time most wisely spent.

Then we started refactoring and making everything work again. The problem was that time wasn’t on our side. We had about an hour and a half to complete what was supposed to be a 8-hour competition.

Fast-forward to 30 minutes before the submission time. Nearly all the logic “seemed” correct - but there were so many minor bugs that it was impossible to test the code. We were all exhausted at that point. We powered through - fixing all kinds of bugs, one at a time, before finally the code worked.

Until it didn’t.

The output didn’t match the expected output and we realised that we had messed up some of the logging functionality (which was another strict requirement) and we still had to make our entire system asynchronous. This is when a jolt of motivation hit me - I remember thinking to myself “There’s no way I’m submitting something that doesn’t work perfectly”.

I implemented the entire multi-threading functionality (thanks to my recent Operating System course at NUS for teaching me about mutexes, critical sections, and concurrent programming) with about 3 minutes to spare. But since I was coding a concurrent program in python literally for the first time in my life (yeah, not the best time to try out new stuff but I didn’t have a choice - even my other 2 teammates didn’t know it), there were some other bugs that had crept up.

With 2 minutes on the clock, I rushed (felt like I was typing at 150 WPM but I’ll never be able to prove it), I continued to fix the bugs and run the tests one by one, until everything worked as expected. We had about 20 seconds left when I committed the latest changes, pushed the code, and closed our laptops.

And that was it.

I really can’t explain the amount of adrenaline pumping through my veins at that point - I loved every moment of the last 30 minutes. The satisfaction in delivering a working product under unbelievably high time pressure (imagine 6 people standing behind you, staring at your screen, hoping you’re able to fix the problem, while there’s a minute left on the clock). is simply ineffable (in fact, I think I’m addicted to working in high-stakes fast-paced environments).

Needless to say, we didn’t expect to win. But to our greatest astonishment, we came 2nd in our category! It turns out that most of the other teams couldn’t successfully make their application multi-threaded either, and although our code quality wasn’t great, our application satisfied their requirements.

All this taught me a whole bunch of lessons:

1. Spend as long as you need clarifying high-level software architecture - make sure each and every person on the team knows exactly what is his/her role as well as how it ties into the bigger system. It’ll save a lot (really, a LOT) of backpedaling down the road and having to start over.
2. Being able to debug code is equally (maybe even more!) as important as being able to code - in real life, you’re mostly going to be working with other people’s code and building on top of it (or reading your own previously written code which you’ll obviously forget how it works)
3. I can’t emphasize enough the importance of good, clean, and elegant code - bad code can literally make your (or others’) head hurt and is frustrating to read. Set incredibly high standards for yourself and others while coding (at least when you have the time to do so). Think of coding as a social activity - you’re not coding for yourself (unless it’s your own pet project, in which case you might still be coding for your future self, who is likely to not understand your terrible code either) - people will be eternally grateful to you for writing good code.
4. Plan, Plan, Plan! Never just start coding directly - use a pen and paper to write down exactly what you’re going to implement, how you’re going to do it - until you’re all confident it will work. Then, the amount of time required to code is directly proportional to your typing speed, and not your thinking speed (because you’ve already thought about everything and, hopefully, written everything down too). Also, aim to finish at least an hour before the submission so you have enough time for testing, improving code quality, preparing a presentation deck, whatever - ideally there should be no functional changes 1 hour before the submission.
5. Learn to deal with high-pressure situations - it’s an incredibly useful skill and I’m super grateful to be able to remain calm in such situations.
6. Software Engineering is about COMMUNICATING computational ideas - during the span of 8 hours, I spoke to a lot different of people including mentors regarding our code and the problems that we were facing - the only important skill in order to even get help from them was to be able to communicate what we were trying to achieve at the right level of abstraction. Remember, coding is all about abstractions and software engineering requires being able to communicate these abstractions.
7. Lastly, learn to despise the big bang - don’t make the mistake of waiting till all your components are built before integrating them together into a complete working system. Build your code incrementally (aka iteratively) and integrate continuously - at every step, make sure you have a working product that has some subset of features/functionality. A working cycle is better than a hypothetical car - at least you can reach your destination.

All in all, yes, I made tons of mistakes, learned a lot from them, and overall, had an awesome time today! Now, it’s been a long day, and I’m going to sleep. 💤
