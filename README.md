# Idle Bank Tycoon — Independent Economy Design Study

Two proposals: a temporary **Loan Desk liquidity lock** and **income-scaled rewarded ads**. The workbook separates soft currency, premium-currency consumption and additional cash receipts, with adjustable assumptions and a proposed experiment. No internal Kolibri telemetry or measured commercial lift is claimed.

[Read the case study](https://merogith.github.io/IdleBankTycoonCaseStudy/) · [Download the workbook](./Idle_Bank_Tycoon_Economy_Model.xlsx) · [Read the PDF](./docs/case-study.pdf)

## Try the model in two minutes

1. Open **Parameters**. Blue cells are active inputs with unit bounds.
2. Set additional paid replenishment from 25.0% to 0%: Loan Desk cash becomes zero while 180,000 ingots/day are still consumed.
3. Try the fixed reference: 4h term, 12h buffer, 40% principal, 10% maturity interest and a 50% limit. Multiplier 1.35 gives 47% and PASS; the original 1.50 candidate gives 62% and BREACH. Current outputs below use the current JSON inputs.
4. Set extra-slot buyer share to 2%, then change slot price. Inspect premium consumption, cash conversion and the daily slot capacity warning independently.

## Current illustrative scenario

| Quantity | Output | Interpretation |
|---|---:|---|
| Soft boost plus maturity interest / normal term income | 47.0% | PASS against the current 50.0% threshold; not proof of safe progression |
| Premium currency consumed | 180,000 ingots/day | A currency sink |
| Retail-equivalent value consumed | $1,800/day | **Not cash receipts** |
| Loan Desk incremental cash scenario | $157.50/day | Retail equivalent × 25.0% additional paid replenishment × 70.0% net realization × 50.0% after substitution |
| Rewarded-ad receipt change | $3,795/day | Assumes views/watcher change from 6 to 8.5; response is unmeasured |
| Scenario blended cash ARPDAU | $0.1998 | Assumed baseline $0.1800; static population |
| Annualized combined cash scenario | $1,442,662 | Arithmetic under assumptions, not a forecast |

At zero additional paid replenishment, Loan Desk cash is zero. Zero/10%/25%/50% replenishment reference cases appear in KPI Impact. Ad-view response can also be zero or negative; change the scenario views input. No retention gain is monetized. No external ad-lift floor or measured response is assumed. Ad starts are multiplied by completion before applying completed-view eCPM.

## Design and balance

Principal returns at maturity. The temporary boost **plus maturity interest is a soft-currency faucet**; ingot fees and optional extra slots are the premium-currency sink. The current multiplier is 1.35× and the term is 4h, including 10.0% maturity interest in the reward review. The fixed 4h reference above explains why the original 1.50× candidate was retuned to 1.35× at the committed reference settings.

Proposed implementation: one active loan, no multiplier stacking, sequential daily slots, at most one extra paid slot. A static full-use daily ceiling and slot-capacity warning are shown; impossible extra-slot spending is excluded from currency and cash calculations. The model does not simulate active upgrading, reinvestment, prestige or early-repayment timing. The current baseline uses 50 soft/sec, 100 base upgrade cost, 1.18× income growth and 1.21× cost growth across 60 levels; those toy values do not prove a meaningful late-game liquidity sacrifice. Actual balances and progression telemetry must establish that premise.

## Proposed experiment

Randomize **at feature eligibility**, not merely at install: established players reaching the Loan Desk for A, and eligible ad-watchers for B, in separate control-versus-treatment experiments. Stratify platform/progression, avoid overlapping economy treatments, and measure 14-day net receipts per assigned eligible player. Day-1/day-7 post-exposure return are guardrails, not install retention.

Before enrollment, estimate player-level variance from a pilot and size a 3% relative minimum detectable effect at 80% power and two-sided alpha 0.05. Fix the sample size/analysis, cover weekly cycles and finish every 14-day follow-up. Proposed non-inferiority thresholds to agree before launch: return-rate lower confidence bound above −1 percentage point and session-length ratio lower bound above 0.95. Check currency sourcing, progression and complaints. Ship only with positive revenue evidence and guardrails met; otherwise iterate or stop. Additional variants need a multiple-comparison plan. No unsupported numerical sample-size estimate is supplied.

## Rebuild and verify

Python 3.12; install `pip install -r requirements-build.txt`. Chrome/Chromium is needed for the PDF, and LibreOffice is used by the optional recalculation check.

```bash
python scripts/build_model.py       # workbook, charts, HTML, README and metrics from model-inputs.json
python scripts/build_pdf.py         # PDF rendered from the generated HTML; records artifact hashes
python scripts/verify_model.py      # arithmetic, active inputs, formulas, PDF links and freshness
python scripts/verify_model.py --recalculate  # also change inputs in disposable workbooks and recalculate with LibreOffice
```

Edit `model-inputs.json` for default scenarios, `case-study.template.html` for prose, and `README.template.md` for this document. The seven workbook tabs retain the baseline/Loan Desk/ad/KPI workflow. Cached formula values support previewers; Excel/LibreOffice recalculates edited inputs. Reference-case fractions in the scenario table are fixed comparison cases, not hidden live inputs.

The [official publisher website](https://www.kolibrigames.com/) is background only. All model numbers are labelled assumptions; no calibrated internal game data or verified third-party numerical benchmarks are represented. Real deployment needs measured calibration, implemented progression/stacking rules and the proposed experiment.

**Meriç Erler** · Berlin · [Full portfolio](https://merogith.github.io/Portfolio/)
