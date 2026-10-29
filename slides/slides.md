---
theme: mokkapps
title: From PDF to Structure
info: |
  How a document layout analysis service turns a flat PDF into usable structure.
  Demo: A/HRC/PRST/35/1 (68548.pdf).
class: text-center
highlighter: shiki
lineNumbers: false
drawings:
  persist: false
transition: slide-left
mdc: true
layout: cover
---

# From PDF to Structure

## What document segmentation actually solves

<small class="opacity-60">Demo document: A/HRC/PRST/35/1 — 3 pages, 52 segments</small>

<!--
Open with the problem everyone in the room has felt: you get a PDF and you need to use it.
No technology yet, no how-to.
-->

---
layout: intro
---

# A PDF is a picture of a document

To a computer, a PDF is not a report with headings and paragraphs. It is ink placed at coordinates
on a page.

- Nothing says *this is a title*
- Nothing says *these lines are one paragraph*
- Nothing says *read this first*

<div class="pt-6 opacity-70 text-base">
Open a PDF in any text viewer and you get the words — just not the document.
</div>

<!--
One sentence that has to land: the file stores positions, not meaning.
-->

---
layout: intro
---

# Segmentation restores the meaning

<div class="grid grid-cols-3 gap-10 w-full pt-4">

<div>
<h3 class="opacity-100 mb-3">Extent</h3>
<p class="text-lg mt-0">Which words belong together, as one block?</p>
</div>

<div>
<h3 class="opacity-100 mb-3">Type</h3>
<p class="text-lg mt-0">Is it a title, a heading, a paragraph, a table, a picture?</p>
</div>

<div>
<h3 class="opacity-100 mb-3">Order</h3>
<p class="text-lg mt-0">What does a person read first, second, third?</p>
</div>

</div>

<div class="pt-16 text-2xl text-center">
The service answers all three — page by page, in one pass.
</div>

<!--
The whole idea in one slide: three questions, three answers.
Do not go deeper unless asked.
-->

---
layout: intro
---

# It uses AI, and it looks at the page

<div class="grid grid-cols-2 gap-16 w-full pt-4">

<div>
<h3 class="opacity-100 mb-3">Visual</h3>
<p class="text-lg">It <em>sees</em> each page — a masthead, an emblem, a table, the shape of a
paragraph. The same cues a person uses at a glance.</p>
</div>

<div>
<h3 class="opacity-100 mb-3">Semantic</h3>
<p class="text-lg">It also <em>reads</em> the words, so it can tell a heading from body text by
what they say, not only by where they sit.</p>
</div>

</div>

<div class="pt-16 text-xl center opacity-80">
A trained model combines both signals, draws one box around each piece of the page,<br/>
and gives every box a type.
</div>

<!--
Two signals. That combination is why it handles a masthead or a scanned table far better than
hand-written rules. No model names, no architecture — purpose only.
-->

---

# Input: a PDF. Output: a structured document.

<div class="grid grid-cols-2 gap-10 pt-4">
<div class="text-center">
<img src="/assets/overlay/input-p1.png" class="h-[430px] mx-auto shadow" />
<p class="text-xs opacity-60 mt-2">Input — an ordinary 3-page PDF</p>
</div>
<div class="text-center">
<img src="/assets/overlay/output-p1.png" class="h-[430px] mx-auto shadow" />
<p class="text-xs opacity-60 mt-2">Output — every block located and labelled</p>
</div>
</div>

<!--
Same page twice: left is what you give it, right is what you get back.
Colours are only labels — each box is one piece of the document, named.
-->

---

# The close-up: labels, not guesswork

<img src="/assets/detail-band.png" class="w-[85%] mx-auto shadow" />

<p class="text-sm opacity-70 pt-8 center">
To the file this is just ink. To the service it is a running title, an emblem, and a
distribution block — numbered in the order a person would read them.
</p>

<div class="grid grid-cols-3 gap-4 pt-8 text-sm center">
<div><b>Page header</b><br/><span class="opacity-60">the running title</span></div>
<div><b>Picture</b><br/><span class="opacity-60">the emblem and its wordmark</span></div>
<div><b>Text</b><br/><span class="opacity-60">the distribution block</span></div>
</div>

<!--
Replaces the distorted close-up: natural aspect, full width, nothing stretched.
Point at one heading and one paragraph — the model separated them, it did not just cut the page.
-->

---
layout: intro
---

# Then most jobs become a filter

Every block already carries a type. Choosing what you need is just selecting a type.

<div class="grid grid-cols-2 gap-14 pt-10">

<div>
<h3 class="opacity-100 mb-2">Table of contents</h3>
<p class="text-base">Keep the headings, drop everything else. The outline of the document, without
reading it.</p>
</div>

<div>
<h3 class="opacity-100 mb-2">Paragraphs</h3>
<p class="text-base">Keep the running text, drop headers, footers and page numbers. Content you can
actually read.</p>
</div>

</div>

<div class="pt-12 text-base opacity-70 center">
Same segmentation. Different filter. Nothing is analysed twice.
</div>

<!--
Payoff slide. Say plainly: it is filtering, not new work.
-->

---

# Filter: headings → table of contents

<div class="grid grid-cols-2 gap-14 items-center h-[85%]">

<div>
<img src="/assets/filter-toc.png" class="h-[21rem] w-auto mx-auto" />
<div class="text-xs opacity-60 text-center pt-3 mx-auto max-w-sm">Only the headings kept — everything else faded out.</div>
</div>

<div>

<div class="text-lg font-600 pb-4">The outline of the document:</div>

<div class="space-y-4 text-base">
<div class="border-l-4 pl-4" style="border-color:#C70039">Human Rights Council — Thirty-fifth session</div>
<div class="border-l-4 pl-4 ml-6" style="border-color:#C70039">President's statement</div>
<div class="border-l-4 pl-4 ml-12" style="border-color:#C70039">PRST 35/1. Situation of human rights in Côte d'Ivoire</div>
</div>

<div class="text-xs opacity-60 pt-8">
Three headings, three levels. The service also returns which heading sits under which.
</div>

</div>
</div>

<!--
Left: same page, only headings kept. Right: those headings as text.
This is the real table-of-contents response for this document.
-->

---

# Filter: body text → clean paragraphs

<div class="grid grid-cols-2 gap-14 items-center h-[85%]">

<div>
<img src="/assets/filter-text.png" class="h-[21rem] w-auto mx-auto" />
<div class="text-xs opacity-60 text-center pt-3 mx-auto max-w-sm">Only the running text kept — headers, footers and page numbers faded out.</div>
</div>

<div>

<div class="text-lg font-600 pb-4">The content of the document:</div>

<div class="p-5 rounded bg-black/5 text-sm leading-relaxed">
At the 37th meeting, held on 23 June 2017, the President of the Human Rights Council made the
following statement: "The Human Rights Council, 1. Thanks the Independent Expert on the
enhancement of capacity-building and technical cooperation with Côte d'Ivoire…
</div>

<div class="text-xs opacity-60 pt-8">
Each paragraph arrives on its own, in reading order — not as one wall of text.
</div>

</div>
</div>

<!--
Same page, other filter. The quote is the actual extracted text.
-->

---

# One analysis, many outputs

<div class="grid grid-cols-4 gap-6 pt-6">

<div class="p-6 rounded border h-40">
<h3 class="opacity-100 mb-1">Outline</h3>
<p class="text-sm mt-0">headings only</p>
</div>

<div class="p-6 rounded border h-40">
<h3 class="opacity-100 mb-1">Text</h3>
<p class="text-sm mt-0">paragraphs only</p>
</div>

<div class="p-6 rounded border h-40">
<h3 class="opacity-100 mb-1">Figures</h3>
<p class="text-sm mt-0">pictures and tables only</p>
</div>

<div class="p-6 rounded border h-40">
<h3 class="opacity-100 mb-1">Markdown</h3>
<p class="text-sm mt-0">the document, rebuilt</p>
</div>

</div>

<div class="pt-14 text-2xl">
Segment once. Then choose what you need.
</div>

<div class="pt-6 text-base opacity-60">
The expensive step — understanding the page — happens once. Everything after it is selection.
</div>

<!--
Close the argument: the expensive step happens once, the filters are cheap. That is why the
feature exists.
-->

---
layout: section
---

# A PDF you can work with

Not a picture of a document — a document.

<!--
Final thought. No call to action, no UI instructions.
-->
