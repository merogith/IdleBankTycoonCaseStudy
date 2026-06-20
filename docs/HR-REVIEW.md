# HR Review — Idle Bank Tycoon Economy Design Case Study

*Reviewer lens: senior hiring reviewer for a Game Economy Designer role. Allergic to AI-polished prose, clichés, and claims that don't survive a second read. Reviewing both the website (`idle-bank-tycoon.html`) and the `README.md`.*

---

## Verdict

The craft and the economic literacy are real. Two things hold it back from a discerning reviewer: (1) the centrepiece feature is **mislabelled** in a way a Game Economy Designer specifically should not get wrong, and (2) the prose carries the **tell-tale cadence of AI-assisted writing**, which — for an AI-averse reader — quietly erodes the "this is *my* judgment" signal the whole document depends on. Both are fixable without redoing the work. This is an **interview-worthy** candidate whose case study needs one revision pass before it circulates.

## What is genuinely strong (credit where due)

- **Engineering of the page** — single self-contained HTML; charts embedded as base64 (won't break when emailed); all three images carry descriptive `alt` text; `:focus-visible`, `prefers-reduced-motion`, and print styles present; coherent design tokens.
- **Intellectual honesty is present** — assumptions labelled, sources on a separate tab, "none of the figures are Kolibri's internal data" stated plainly.
- **The arithmetic that is shown is internally consistent** (verified): `6,075/s × 43,200s = $262M`; `40% = $105M`; `1.5× → 9,113/s`; boost differential `= $43.7M = 50%` of normal 4h earnings; `8.5/6.0 = +41.7%`; `$0.028 × 200k × 365 ≈ $2M`.
- **Domain vocabulary used correctly** — source/sink, prestige, Weber–Fechner, eCPM, platform-split A/B, retention-vs-ARPU trade-off, install-time assignment.

## Issues found

### A. Economics (the ones that matter)
1. **The "soft-currency sink" is actually a soft-currency *faucet*.** The diagnosis says players drown in idle cash. The "fix" locks cash for 4h, **returns the full principal**, and **adds a +50%-of-earnings boost (+$43.7M)** plus a soft bonus. Net soft currency to the player is *positive* — the feature creates currency. The only genuine sink is the **hard-currency** ingot accelerators (valued by the model itself at a trivial **$0.009 ARPDAU**). Guardrail #6 — *"Soft interest is low, so the Loan Desk drains cash on net"* — directly contradicts a 50% boost.
2. **The +41.7% hero number rests entirely on an unsourced assumption.** `8.5/6.0 = +41.7%` *is* the assumed jump in opt-in views. The only **sourced** effect (+23% interstitial resequencing) appears nowhere in the number, yet the copy says "together they give +41.7%."
3. **The interstitial-after-rewarded tactic threatens the retention the doc keeps guarding.** "No added frustration / no extra ad load" is asserted, not evidenced, and sits awkwardly next to the retention-guardrail emphasis.
4. **The feature's stated main purpose (D7 lift) is entirely unmodelled** — hand-waved, while the quantified part ($0.009) is negligible.

### B. AI-voice tells
5. **The "X, not Y" antithesis is a verbal tic — 9 times in ~1,400 words** ("ad-led, not whale-led," "efficiency, not acquisition," "ratios, not absolutes," "an assumption, not a result," "the method, not the specific figures," …). At this density it's the unmistakable rhythm of generated prose.
6. **Triads everywhere** and **tidy closing aphorisms** ("a feature players experience as generous that still drains more currency than it grants"). Too smooth, too balanced.
7. **Cliché / jargon load** — "single source of truth" (×2), "make the rewarded economy work harder," "end to end," "fastest revenue lever," and **"lever" ~10 times**.

### C. Framing / honesty calibration
8. **All three hero stats trace to the same assumption set**, but the caveats live in footnotes while the banner reads like findings.
9. **Everything hangs off one "~level-30 player"**; the sensitivity grid covers adoption × spender share, not the loan parameters a designer actually tunes.

### D. Craft nits
10. **Accessibility** — muted grey `#7c7d82` at 12–13.5px computes to **4.00:1** contrast, **failing WCAG AA** (needs 4.5:1). Everything else passes.
11. **The two CTAs behave inconsistently** — `.xlsx` force-downloads; PDF opens GitHub's viewer. Both resolve (files verified on `main`), but "Download" should download.

---

## Recommendations — as a multiple-choice questionnaire

Each question lists options; ✅ marks the recommended pick, followed by the rationale. *(All ✅ options have been applied in this revision — see the changelog at the foot of this file.)*

### Q1. The "soft-currency sink" that adds soft currency
- A. Leave it.
- **B. ✅ Relabel and resolve the contradiction** — rename it an engagement/liquidity mechanic with a hard-currency sink; either make the soft economics net-negative or stop calling it a soft sink; fix guardrail #6.
- C. Keep the name, add a footnote.
- D. Cut the boost entirely.

*Why B:* the one error that reads as a competency gap for an economy role; the fix converts the biggest liability into a demonstration of exactly the sink/faucet discipline the job tests.

### Q2. The +41.7% headline resting on an unsourced assumption
- A. Keep +41.7% as the banner.
- B. Drop the rewarded section.
- **C. ✅ Demote and split it** — lead with the +23% sourced effect; show +41.7% as a clearly-labelled modelled upside; let the A/B test settle it.
- D. Re-derive from a sourced benchmark.

*Why C:* trust collapses the moment the flagship number turns out to be an assumption dressed as a result. Separating sourced from speculative protects the candidate.

### Q3. Three hero stats with caveats buried in footnotes
- A. Keep as is.
- **B. ✅ Put the honesty on the surface** — one-line "modelled on labelled estimates, not Kolibri data" next to the hero band; mark sourced vs modelled inline.
- C. Remove two of the three stats.
- D. Replace stats with a method statement.

*Why B:* the honesty is a strength that's currently hidden; surfacing it turns "overclaiming" into "disciplined."

### Q4. The "X, not Y" antithesis (9 occurrences)
- A. Leave it.
- **B. ✅ Cut to 2–3 and vary the sentence shapes.**
- C. Replace all with em-dash asides.
- D. Run it through another paraphraser.

*Why B:* the loudest "AI wrote this" signal in the document; breaking the rhythm does more for authenticity than any other edit.

### Q5. Cliché / jargon density
- A. Keep — industry vocabulary.
- **B. ✅ Prune ruthlessly** — kill "single source of truth," "work harder," "end to end"; halve "lever"; use concrete nouns.
- C. Add a glossary.
- D. No change.

*Why B:* specific words read as expertise; filler reads as padding — the cheapest credibility gain available.

### Q6. "No added frustration / no extra ad load"
- A. Keep the claim.
- **B. ✅ Soften and guard it** — "directionally positive; must be validated against D1/session length as a hard guardrail"; name it as the risk in the A/B plan.
- C. Drop the interstitial tactic.
- D. Claim it improves UX.

*Why B:* the doc's credibility comes from retention caution; an unguarded "no frustration" claim contradicts that posture.

### Q7. The unmodelled D7 lift (the feature's "main purpose")
- A. Keep asserting it.
- **B. ✅ Quantify a plausible band** — "if D7 moves +1–2pt, ≈ $X, an order of magnitude above the $0.009 sink."
- C. Stop calling it the main purpose.
- D. Move it to future work.

*Why B:* the feature is justified by the number it *doesn't* show and undercut by the number it *does*; a back-of-envelope band fixes the risk/reward story.

### Q8. Overall voice — how far to rewrite
- A. Light copy-edit only.
- **B. ✅ One pass in the candidate's own voice** — break the parallelism, add one or two personal judgment calls ("I'd ship B first because…"), keep the numbers.
- C. Full rewrite from scratch.
- D. Leave it; substance over style.

*Why B:* for an AI-averse reviewer, a human voice with one or two opinions beats flawless balanced prose; C wastes solid scaffolding.

### Q9. Accessibility — muted text at 4.00:1
- A. Ignore.
- **B. ✅ Darken `--muted` to ~`#6b6c70`** (≈5.1:1).
- C. Increase those font sizes to 18px+.
- D. Leave it.

*Why B:* a two-character CSS change clears a real standard; shipping a measurable a11y fail on a rigour pitch is an unforced own-goal.

### Q10. Single worked example, no loan-parameter sensitivity
- A. Keep one example.
- **B. ✅ Add early/late rows and a small sensitivity on the loan params** (multiplier, boost, term).
- C. Add more prose.
- D. No change.

*Why B:* sensitivity is the case study's stated strength; right now it's applied to monetisation knobs but not design knobs.

### Q11. "Prepared for Kolibri Games" + their IP next to speculative numbers
- A. Remove the company framing.
- **B. ✅ Keep it, add one prominent early disclaimer** — "Independent, unsolicited; public estimates only; not affiliated with Kolibri."
- C. Anonymise the game.
- D. No change.

*Why B:* the initiative is a hiring plus; one early disclaimer neutralises the only risk. Anonymising throws away the strongest signal — genuine interest in *this* game.

---

## Changelog (applied in this revision)

- **Q1** — Section retitled "a liquidity lock with a hard-currency sink"; intro now states the soft side is "deliberately a faucet, not a sink"; guardrail #6 rewritten to stop claiming a net soft drain; closing callout reframed around the soft-boost/hard-sink split.
- **Q2** — Hero metric and Opportunity-B copy now lead with the sourced **+23%** and present **+41.7%** as a modelled ceiling; the B-outcome cell reads `+23%→41.7%`.
- **Q3 / Q11** — A prominent `hero-note` disclaimer added under the metric band (independent/unsourced/modelled, not Kolibri data); sourced-vs-modelled flagged inline.
- **Q4** — "X, not Y" reduced from 9 to 2 deliberate instances; the rest rewritten as plain declaratives.
- **Q5** — "single source of truth," "work harder," "end to end," "fastest revenue lever" removed; "lever" roughly halved.
- **Q6** — "no added frustration / no extra ad load" softened to "no new forced ad breaks"; interstitial named as the main retention risk and gated by a D1/session-length guardrail in the A/B plan.
- **Q7** — Combined-impact paragraph now gives a rough D7 value band ($0.005–$0.02 ARPDAU-equivalent for +1pt D7) and states A is shipped to *measure* it.
- **Q8** — Personal sequencing judgment added ("ship B first … treat A as the bigger retention bet"); parallelism broken throughout.
- **Q9** — `--muted` darkened `#7c7d82 → #6b6c70` (4.00:1 → ~5.1:1).
- **Q10** — Worked-example note adds early (~Bank 10) and late (~Bank 50) illustrations and a stress-test of the loan design knobs (boost 1.25–2.0×, term 2–8h, principal 25–50%).

*Note: the same guardrail-#6 wording also lives in the `.xlsx` Loan Desk tab and should be corrected there to match.*
