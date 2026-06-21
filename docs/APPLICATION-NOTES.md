# Application Notes — Game Economy Designer, Kolibri Games

Internal notes on how these documents are built and how to submit them, so the CV and cover
letter clear automated pre-screening *and* read as genuinely human to an AI-averse reviewer.

## Two versions of each document, on purpose

| Document | File | Use it for |
|---|---|---|
| Designed CV | `cv.html` → print to PDF | The human/portfolio copy. Attach when emailing a person, or link. |
| Designed cover letter | `cover-letter.html` → print to PDF | Same — the on-brand copy. |
| **ATS CV** | `Meric_Erler_CV.pdf` / `.docx` | **Upload into the application form** (Lever, etc.). |
| **ATS cover letter** | `Meric_Erler_Cover_Letter.pdf` / `.docx` | **Upload into the application form.** |

The designed files use a custom layout and web fonts that look great but are slightly riskier for
a parser. The ATS files are single-column, standard-font (Arial), plain-bullet, ASCII-safe — they
extract cleanly top-to-bottom. Both carry the same facts and keywords.

> To print the **designed** PDFs: open `cv.html` / `cover-letter.html` in Chrome → Print →
> Save as PDF → A4. (Each is tuned to one page.)
>
> To rebuild the **ATS** PDFs/DOCX: `python3 scripts/build-ats-docs.py` (needs `reportlab` and
> `python-docx`). Source content lives in `cv-ats.html` / `cover-letter-ats.html` for reference.

## Why it's built this way

**ATS / parser pre-screening.** Kolibri recruits via Lever, whose parser handles clean text PDFs
well. The ATS copies are single column with no tables, no multi-column blocks, and no text-in-
images, so the name, sections and dates parse in the right order. Verified by extracting the PDF
text layer — it comes out clean and complete.

**AI / LLM screeners.** These rank on *relevant specificity*, not keyword density. The role's
vocabulary is woven in where it's actually backed by work: economy balancing, sources/sinks,
inflation control, progression curves, monetization (IAP, rewarded ads, ARPDAU/ARPPU/eCPM),
retention (D1/D7/D30), player psychology and segmentation, A/B testing, sensitivity analysis,
Excel & Google Sheets, data analysis, F2P. No stuffing.

**The AI-averse human reviewer.** AI-detection tools are unreliable and rarely gate hiring, so the
real target is the *reading experience*. Edits removed the tells the genre is known for: em-dash
asides in prose, the "X, not Y" antithesis rhythm, tidy triads, repeated phrasing across the two
documents, and uniform sentence length. The voice is first-person with a couple of genuine
opinions (e.g. "ship the ad tuning first, treat the loan as the bigger retention bet") — the kind
of judgement an LLM doesn't invent.

## German / Berlin norms (English-language application to an international studio)

- **No photo, no date of birth, no signature.** Correct for an English CV to an international
  Berlin studio, and safer under EU anti-discrimination norms.
- **One page**, reverse-chronological, English. Title the file "CV", not "Lebenslauf".
- Languages listed with proficiency.

## Truthfulness guardrails (kept honest)

- **Unity:** stated only as "concepts that carry over to Unity" — no hands-on claim.
- **Mobile:** framed as "mobile-first / phone-responsive browser games" — not native, not shipped.
- **Case-study numbers:** the study itself labels every figure as modelled on public estimates,
  not Kolibri's internal data.

## Submission checklist

1. Upload `Meric_Erler_CV.pdf` (or `.docx`) and `Meric_Erler_Cover_Letter.pdf` to the form.
2. In the cover letter / message field, link the case study: `merogith.github.io/IdleBankTycoonCaseStudy`.
3. Optionally attach or link the designed PDFs as the portfolio copy.
4. Double-check the role title and that the letter names **Idle Bank Tycoon**.
