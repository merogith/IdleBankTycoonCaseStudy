"""Illustrative economy arithmetic; no game telemetry or measured lift is implied."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# key, display label, units, minimum, maximum, integer
INPUTS = [
    ("income_start", "Starting income", "soft / sec", 0.01, 1e9, False),
    ("income_growth", "Income growth per level", "multiplier", 1, 2, False),
    ("cost_start", "First upgrade cost", "soft", 0.01, 1e12, False),
    ("cost_growth", "Cost growth per level", "multiplier", 1, 2, False),
    ("levels", "Levels displayed", "levels (max 120)", 1, 120, True),
    ("example_level", "Representative level", "level (clamped to horizon)", 1, 120, True),
    ("offline_hours", "Offline buffer assumption", "hours", 0.1, 24, False),
    ("dau", "Illustrative daily active users", "players", 1, 1e9, True),
    ("watcher_share", "Share of DAU watching rewarded ads", "fraction", 0, 1, False),
    ("rewarded_ecpm", "Rewarded eCPM", "USD / 1000 completed views", 0, 1000, False),
    ("baseline_views", "Baseline ad starts per watcher/day", "views", 0, 100, False),
    ("tuned_views", "Scenario ad starts per watcher/day", "views (hypothesis)", 0, 100, False),
    ("completion", "Rewarded completion rate", "fraction", 0, 1, False),
    ("reward_minutes", "Instant ad reward", "minutes of current income", 0, 240, False),
    ("ad_boost_hours", "Duration of a separate 2x ad boost", "hours", 0, 24, False),
    ("principal_share", "Principal share of assumed idle buffer", "fraction", 0, 1, False),
    ("loan_hours", "Loan term", "hours", 0.1, 24, False),
    ("loan_multiplier", "Income multiplier during one loan", "multiplier", 1, 3, False),
    ("maturity_interest", "Maturity bonus on returned principal", "fraction", 0, 1, False),
    ("early_fee", "Early repayment fee", "ingots / spending user/day", 0, 10000, False),
    ("free_slots", "Free sequential loans per day", "slots", 1, 24, True),
    ("extra_slot_price", "One extra sequential slot price", "ingots", 0, 10000, False),
    ("adoption", "Loan Desk adoption among DAU", "fraction", 0, 1, False),
    ("early_spender_share", "Loan users paying early-repay fee/day", "fraction", 0, 1, False),
    ("extra_buyer_share", "Loan users buying one extra slot/day", "fraction", 0, 1, False),
    ("ingot_retail", "Ingot retail-equivalent value", "USD / ingot", 0, 100, False),
    ("paid_replenishment", "Burn replenished by additional paid purchases", "fraction (unmeasured)", 0, 1, False),
    ("net_realization", "Realized receipt / retail value", "fraction after discounts/fees", 0, 1, False),
    ("cannibalization", "Replacement of other paid purchases", "fraction of replenishment", 0, 1, False),
    ("baseline_arpdau", "Illustrative baseline blended ARPDAU", "USD / player/day", 0, 1000, False),
    ("max_reward_ratio", "Proposed total bonus / normal-term-income limit", "fraction (design threshold)", 0, 3, False),
]


def defaults():
    return json.loads((ROOT / "model-inputs.json").read_text())


def evaluate(parameters):
    p = dict(parameters)
    for key, _, _, lower, upper, integer in INPUTS:
        value = p[key]
        if not isinstance(value, (int, float)) or not math.isfinite(value) or not lower <= value <= upper:
            raise ValueError(f"{key} must be in [{lower}, {upper}]")
        if integer and value != int(value):
            raise ValueError(f"{key} must be an integer")
    level = min(p["example_level"], p["levels"])
    income = p["income_start"] * p["income_growth"] ** (level - 1)
    buffer = income * 3600 * p["offline_hours"]
    principal = buffer * p["principal_share"]
    normal = income * 3600 * p["loan_hours"]
    boost = normal * (p["loan_multiplier"] - 1)
    interest = principal * p["maturity_interest"]
    total_bonus = boost + interest
    reward_ratio = total_bonus / normal
    loan_users = p["dau"] * p["adoption"]
    extra_capacity = int(math.floor(24 / p["loan_hours"]) > p["free_slots"])
    ingots = loan_users * (p["early_spender_share"] * p["early_fee"] +
                           p["extra_buyer_share"] * p["extra_slot_price"] * extra_capacity)
    retail = ingots * p["ingot_retail"]
    incremental_cash = retail * p["paid_replenishment"] * p["net_realization"] * (1 - p["cannibalization"])
    ad_base = p["dau"] * p["watcher_share"] * p["baseline_views"] * p["completion"] * p["rewarded_ecpm"] / 1000
    ad_tuned = p["dau"] * p["watcher_share"] * p["tuned_views"] * p["completion"] * p["rewarded_ecpm"] / 1000
    ad_delta = ad_tuned - ad_base
    extra_slot_available = int(p["extra_buyer_share"] > 0)
    max_daily_loans = min(p["free_slots"] + extra_slot_available, math.floor(24 / p["loan_hours"]))
    slot_status = "PASS" if p["free_slots"] + extra_slot_available <= math.floor(24 / p["loan_hours"]) else "CAPACITY EXCEEDED"
    return dict(level=level, income=income, buffer=buffer, principal=principal,
                boosted_income=income*p["loan_multiplier"], normal_term=normal,
                boost_bonus=boost, maturity_bonus=interest, total_bonus=total_bonus,
                reward_ratio=reward_ratio, guardrail="PASS" if reward_ratio <= p["max_reward_ratio"] else "BREACH",
                max_daily_loans=max_daily_loans,
                slot_status=slot_status,
                max_daily_bonus_ratio=max_daily_loans*total_bonus/(income*86400),
                loan_users=loan_users, ingots=ingots, retail=retail, incremental_cash=incremental_cash,
                cash_arpdau=incremental_cash/p["dau"], ad_base=ad_base, ad_tuned=ad_tuned,
                ad_delta=ad_delta, combined_daily=ad_delta+incremental_cash,
                combined_annual=(ad_delta+incremental_cash)*365,
                blended=p["baseline_arpdau"]+(ad_delta+incremental_cash)/p["dau"],
                instant_ad_reward=income*60*p["reward_minutes"],
                ad_boost_reward=income*3600*p["ad_boost_hours"])
