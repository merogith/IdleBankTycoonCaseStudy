"""Build the workbook, charts, HTML and README from one labelled scenario."""
from pathlib import Path
import hashlib
import json
import os

os.environ.setdefault("MPLCONFIGDIR", "/tmp/idle-model-matplotlib")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import xlsxwriter

from model import ROOT, INPUTS, defaults, evaluate

SITE = "https://merogith.github.io/IdleBankTycoonCaseStudy/"
WORKBOOK = "Idle_Bank_Tycoon_Economy_Model.xlsx"


def workbook(p, m):
    book = xlsxwriter.Workbook(ROOT / WORKBOOK)
    book.set_properties({"title": "Idle Bank Tycoon — illustrative economy proposal",
                         "author": "Meriç Erler", "comments": "Scenario outputs, not measured commercial lift."})
    title = book.add_format({"bold": True, "font_size": 17, "font_color": "#2f6b4f", "text_wrap": True})
    header = book.add_format({"bold": True, "bg_color": "#e3ece5", "text_wrap": True, "border": 1})
    text = book.add_format({"text_wrap": True, "valign": "top"})
    number = book.add_format({"num_format": "#,##0.00", "valign": "top"})
    percent = book.add_format({"num_format": "0.0%"})
    integer = book.add_format({"num_format": "#,##0"})
    inputfmt = book.add_format({"font_color": "#135db6", "bg_color": "#edf5ff", "num_format": "0.0000"})
    good = book.add_format({"font_color": "#2f6b4f", "bg_color": "#e3ece5"})
    bad = book.add_format({"font_color": "#9b1c1c", "bg_color": "#ffe7e7"})
    sheets = {}
    for name in ("README", "Parameters", "Baseline Economy", "Loan Desk (A)", "Ad Tuning (B)", "KPI Impact", "Sources"):
        ws = book.add_worksheet(name)
        ws.hide_gridlines(2)
        ws.set_column("A:A", 3)
        ws.set_column("B:B", 50)
        ws.set_column("C:D", 21)
        ws.set_column("E:F", 46)
        ws.freeze_panes(5, 2)
        ws.set_landscape()
        ws.fit_to_pages(1, 0)
        sheets[name] = ws

    def heading(ws, value, note):
        ws.merge_range("B2:F2", value, title)
        ws.set_row(1, 38)
        ws.merge_range("B3:F3", note, text)
        ws.set_row(2, 40)

    ws = sheets["Parameters"]
    heading(ws, "PARAMETERS · illustrative assumptions", "Blue values are active scenario inputs. Validation bounds prevent invalid units; they do not establish a safe game balance. Fractions use 0–1. No live game KPIs are claimed.")
    ws.write_row(4, 1, ["Input", "Value", "Unit", "Meaning"], header)
    rows = {}
    for i, (key, label, unit, lower, upper, whole) in enumerate(INPUTS, 5):
        rows[key] = i + 1
        ws.write(i, 1, label, text)
        ws.write_number(i, 2, p[key], inputfmt)
        ws.write(i, 3, unit, text)
        ws.write(i, 4, "Adjustable modelling assumption; not observed telemetry.", text)
        ws.set_row(i, 32)
        ws.data_validation(i, 2, i, 2, {"validate": "integer" if whole else "decimal", "criteria": "between",
                                       "minimum": lower, "maximum": upper, "error_type": "stop",
                                       "error_title": "Outside model bounds", "error_message": f"Use {lower} to {upper} ({unit})."})

    def ref(key):
        return f"Parameters!$C${rows[key]}"

    def record(ws, row, label, formula, cached, unit, note="", fmt=None):
        ws.write(row-1, 1, label, text)
        ws.write_formula(row-1, 2, formula, fmt or number, cached)
        ws.write(row-1, 3, unit, text)
        ws.write(row-1, 4, note, text)
        ws.set_row(row-1, 34)

    ws = sheets["Baseline Economy"]
    heading(ws, "BASELINE · static per-level reconstruction", "This toy curve is not calibrated game telemetry. The default time to afford an upgrade is seconds, so it does not prove a meaningful late-game liquidity sacrifice. No auto-upgrading or prestige simulation is included.")
    ws.set_column("B:H", 23)
    ws.write_row(4, 1, ["Level", "Income / sec (soft)", "Next upgrade (soft)", "Seconds to afford", "Offline buffer (soft)", "Buffer / next cost"], header)
    for level in range(1, 121):
        row = level + 5
        active = level <= p["levels"]
        income = p["income_start"] * p["income_growth"] ** (level-1)
        cost = p["cost_start"] * p["cost_growth"] ** (level-1)
        ws.write_number(row-1, 1, level, integer)
        formulas = [f'{ref("income_start")}*{ref("income_growth")}^(B{row}-1)',
                    f'{ref("cost_start")}*{ref("cost_growth")}^(B{row}-1)', f'D{row}/C{row}',
                    f'C{row}*3600*{ref("offline_hours")}', f'F{row}/D{row}']
        values = [income, cost, cost/income, income*3600*p["offline_hours"], income*3600*p["offline_hours"]/cost]
        for col, formula, value in zip(range(2,7), formulas, values):
            ws.write_formula(row-1, col, f'=IF(B{row}<={ref("levels")},{formula},"")', number, value if active else "")

    ws = sheets["Loan Desk (A)"]
    heading(ws, "A · Loan Desk: liquidity lock + premium-currency consumption", "Principal returns at maturity. Boost plus interest creates soft currency. One loan active at a time; no multiplier stacking. Sequential daily slots are limited by the 24-hour day. These are proposed implementation rules.")
    ws.write_row(4, 1, ["Metric", "Value", "Unit", "Definition / limit"], header)
    records = [
        (6,"Representative level",f'=MIN({ref("example_level")},{ref("levels")})',"level","level","Clamped to the selected horizon."),
        (7,"Income per second",f'={ref("income_start")}*{ref("income_growth")}^(C6-1)',"income","soft/sec","Static income; no progression simulation."),
        (8,"Assumed offline balance",f'=C7*3600*{ref("offline_hours")}',"buffer","soft","Scenario buffer, not observed inventory."),
        (9,"Principal locked",f'=C8*{ref("principal_share")}',"principal","soft","A share of the assumed buffer; game implementation must use actual available cash."),
        (10,"Boosted income/sec",f'=C7*{ref("loan_multiplier")}',"boosted_income","soft/sec","One non-stacking loan."),
        (11,"Normal income over term",f'=C7*3600*{ref("loan_hours")}',"normal_term","soft","Reference flow over the loan duration."),
        (12,"Extra income from boost",'=C10*3600*'+ref("loan_hours")+'-C11',"boost_bonus","soft","Excludes returned principal."),
        (13,"Maturity interest",f'=C9*{ref("maturity_interest")}',"maturity_bonus","soft","Bonus on returned principal."),
        (14,"Total extra soft currency",'=C12+C13',"total_bonus","soft","Includes BOTH boost and maturity interest."),
        (15,"Total bonus / normal term income",'=C14/C11',"reward_ratio","fraction","Compare against the proposed review threshold."),
        (16,"Reward review status",f'=IF(C15<={ref("max_reward_ratio")},"PASS","BREACH")',"guardrail","status","PASS checks this arithmetic threshold only; not proof of retention or anti-cannibalisation."),
        (17,"Maximum sequential loans/day",f'=MIN({ref("free_slots")}+IF({ref("extra_buyer_share")}>0,1,0),INT(24/{ref("loan_hours")}))',"max_daily_loans","loans","One extra slot maximum if offered; no concurrent stacking."),
        (18,"Maximum daily bonus / fixed normal income",'=C17*C14/(C7*86400)',"max_daily_bonus_ratio","fraction","Static full-use ceiling; excludes reinvestment and changing income."),
        (19,"Daily slot schedule status",f'=IF({ref("free_slots")}+IF({ref("extra_buyer_share")}>0,1,0)<=INT(24/{ref("loan_hours")}),"PASS","CAPACITY EXCEEDED")',"slot_status","status","Do not offer more sequential slots than fit without early repayment; timing is outside this model."),
        (21,"Daily Loan Desk users",f'={ref("dau")}*{ref("adoption")}',"loan_users","users","Illustrative adoption."),
        (22,"Premium currency consumed/day",f'=C21*({ref("early_spender_share")}*{ref("early_fee")}+{ref("extra_buyer_share")}*{ref("extra_slot_price")}*IF(INT(24/{ref("loan_hours")})>{ref("free_slots")},1,0))',"ingots","ingots","Expected early fees plus one extra-slot purchase only if it fits the sequential schedule; users can be in both groups."),
        (23,"Retail-equivalent currency consumed/day",f'=C22*{ref("ingot_retail")}',"retail","USD equivalent","NOT cash receipts; can include free currency or paid inventory."),
        (24,"Scenario incremental cash/day",f'=C23*{ref("paid_replenishment")}*{ref("net_realization")}*(1-{ref("cannibalization")})',"incremental_cash","USD net receipts","Unmeasured additional paid replenishment × realization × (1 − substitution)."),
        (25,"Scenario cash ARPDAU",f'=C24/{ref("dau")}',"cash_arpdau","USD/player/day","Only scenario cash may be added to ad receipts; retail-equivalent burn is separate."),
    ]
    for row,label,formula,key,unit,note in records:
        record(ws,row,label,formula,m[key],unit,note,percent if unit=="fraction" else text if unit=="status" else number)
    ws.conditional_format("C16", {"type":"text","criteria":"containing","value":"BREACH","format":bad})
    ws.conditional_format("C16", {"type":"text","criteria":"containing","value":"PASS","format":good})

    ws = sheets["Ad Tuning (B)"]
    heading(ws, "B · Income-scaled rewarded-ad scenario", "Ad starts per watcher are assumptions; completion is multiplied separately before eCPM. No sourced lift or floor is assumed. Placement changes require a separate experiment at the same forced-ad frequency; interstitial revenue is intentionally outside this calculation.")
    ws.write_row(4,1,["Metric","Baseline","Scenario","Definition"],header)
    for row,label,basekey,tunedkey in [(6,"Ad starts per watcher/day","baseline_views","tuned_views")]:
        ws.write(row-1,1,label,text)
        for col,key in [(2,basekey),(3,tunedkey)]:ws.write_formula(row-1,col,'='+ref(key),number,p[key])
    for row,label,formula,value in [(7,"Rewarded receipt/day (baseline)",f'={ref("dau")}*{ref("watcher_share")}*C6*{ref("completion")}*{ref("rewarded_ecpm")}/1000',m["ad_base"]),
                                   (8,"Rewarded receipt/day (scenario)",f'={ref("dau")}*{ref("watcher_share")}*D6*{ref("completion")}*{ref("rewarded_ecpm")}/1000',m["ad_tuned"]),
                                   (9,"Scenario change in rewarded receipts/day",'=C8-C7',m["ad_delta"]),
                                   (12,"Instant ad reward (soft)",f"='Loan Desk (A)'!C7*60*{ref('reward_minutes')}",m["instant_ad_reward"]),
                                   (13,"Extra soft cash from one separate 2x ad boost",f"='Loan Desk (A)'!C7*3600*{ref('ad_boost_hours')}",m["ad_boost_reward"])]:
        record(ws,row,label,formula,value,"USD/day" if row<10 else "soft","Separate reward options; stacking with loans is not assumed.")

    ws = sheets["KPI Impact"]
    heading(ws,"CASH SCENARIOS · retail-equivalent burn kept separate", "These are adjustable scenarios at static DAU, not forecasts or measured revenue. Zero replenishment means zero incremental Loan Desk cash, even when ingots are consumed. Ad-view response can also be zero or negative.")
    ws.write_row(4,1,["Metric","Value","Unit","Interpretation"],header)
    for row,label,formula,key,unit in [
        (6,"Loan retail-equivalent burn/day","='Loan Desk (A)'!C23","retail","USD equivalent"),
        (7,"Loan incremental cash scenario/day","='Loan Desk (A)'!C24","incremental_cash","USD/day"),
        (8,"Rewarded-ad cash change/day","='Ad Tuning (B)'!C9","ad_delta","USD/day"),
        (9,"Combined cash change/day","=C7+C8","combined_daily","USD/day"),
        (10,"Annualized cash scenario","=C9*365","combined_annual","USD/year"),
        (11,"Scenario blended cash ARPDAU",f'={ref("baseline_arpdau")}+C9/{ref("dau")}',"blended","USD/player/day")]:
        record(ws,row,label,formula,m[key],unit,"Annualization holds population and behavior fixed; no retention value is monetized.")
    ws.write_row(13,1,["Additional paid replenishment","Fraction","Loan cash/day","Combined cash/day","Annualized combined"],header)
    for row,(label,share) in enumerate([("Zero",0),("Low",0.10),("Illustrative",0.25),("High",0.50)],15):
        ws.write(row-1,1,label,text);ws.write_number(row-1,2,share,percent)
        cash=m["retail"]*share*p["net_realization"]*(1-p["cannibalization"])
        ws.write_formula(row-1,3,f'=$C$6*C{row}*{ref("net_realization")}*(1-{ref("cannibalization")})',number,cash)
        ws.write_formula(row-1,4,f'=D{row}+$C$8',number,cash+m["ad_delta"])
        ws.write_formula(row-1,5,f'=E{row}*365',number,(cash+m["ad_delta"])*365)
    ws.merge_range("B20:F21", "Scenario comparison fractions are fixed reference cases, not extra live inputs. Change Parameters to tune the selected scenario. Fixed reference example only: at 4h term, 12h buffer, 40% principal and 10% maturity interest, 1.50x gives 62% and 1.35x gives 47% versus a 50% review threshold. Current scenario inputs/outputs are on Parameters and Loan Desk.",text)
    ws.merge_range("B23:F25", "A/B eligibility: randomize established players when they first reach the Loan Desk. For ad sizing, randomize eligible ad-watchers separately, stratified by platform and progression band. Start with control vs one treatment; no overlapping economy tests. Measure 14-day net receipts per assigned eligible player and day-7 return after exposure; do not call that install D7.",text)
    ws.merge_range("B27:F29", "Before enrollment, size the test using pilot variance and a 3% relative receipts MDE, 80% power, two-sided alpha 0.05. Fix sample size and enroll long enough to cover weekly cycles, then complete 14-day follow-up. Example guardrails to confirm with owners: day-1/day-7 post-exposure return non-inferiority margin −1 percentage point, session-length ratio lower bound 0.95. Ship only with positive revenue evidence and guardrails met; otherwise iterate or stop. Thresholds are proposed, not measured.",text)

    ws=sheets["Sources"]
    heading(ws,"ASSUMPTIONS, SCOPE AND BACKGROUND","All numerical inputs are illustrative. No internal Kolibri telemetry, guaranteed ad uplift, verified retention benchmark or measured incremental purchase behavior is represented.")
    for row,(label,note) in enumerate([
        ("Publisher background", "Kolibri Games official website; game/publisher context only, no numeric calibration."),
        ("Removed untraceable benchmarks", "The prior +23% ad floor and 73 videos/user claims lacked a specific study/time window. They are not used or presented as evidence."),
        ("Static baseline", "Income/cost growth, starting amounts and offline buffer are toy assumptions, not a recovered live progression curve."),
        ("Cash conversion", "Additional paid replenishment, net realization and substitution must be estimated from an experiment or transaction telemetry."),
        ("Balance limit", "The total-reward threshold is a proposed design control, not an empirical guarantee of non-cannibalisation or fairness."),
        ("Economic scope", "Principal returns; soft bonus is a faucet. Premium-currency consumption is a sink; its retail equivalent is not new cash."),
        ("No production claim", "The model lacks live calibration, progression simulation, currency inventory cohorts, operating costs and measured retention/LTV."),
    ],6):
        ws.write(row-1,1,label,header);ws.merge_range(row-1,2,row-1,5,note,text);ws.set_row(row-1,58)
    ws.write_url("C6","https://www.kolibrigames.com/",string="Official publisher background")

    ws=sheets["README"]
    heading(ws,"IDLE BANK TYCOON · independent economy proposal","Two concepts: a temporary liquidity-lock loan and income-scaled rewarded ads. A reproducible scenario workbook, not a claim of validated commercial lift.")
    notes=[
        "Start on Parameters. Every blue cell is an active input, with valid-unit bounds. Calculated cells use formulas and carry cached default values for previewers.",
        "Follow Baseline Economy → Loan Desk (A) → Ad Tuning (B) → KPI Impact. USD cash, USD retail-equivalent and soft currency have distinct units.",
        "Try: set paid replenishment to 0%. Loan cash becomes zero while currency consumption stays unchanged.",
        "Try the fixed reference: 4h term, 12h buffer, 40% principal, 10% maturity interest and 50% threshold. A 1.50 multiplier yields 62% and BREACH; 1.35 yields 47% and PASS. Current outputs always reflect Parameters.",
        "Try: set extra-slot buyer share to 2%, or change extra-slot price, free daily slots, level horizon or reward duration. The related outputs respond; no unused benchmark controls remain.",
        "One active loan, no multiplier stacking, sequential slots only, and at most one paid extra daily slot. These are proposed rules; the sheet is not a gameplay implementation.",
        "KPI Impact compares zero/low/illustrative/high additional paid-replenishment assumptions. These scenarios do not establish a lower bound; ad response is also uncertain.",
        "Source inputs: model-inputs.json. Build: python scripts/build_model.py; then python scripts/build_pdf.py. Verify: python scripts/verify_model.py. See Sources for limits."
    ]
    for row,note in enumerate(notes,6):
        ws.merge_range(row-1,1,row-1,5,note,text);ws.set_row(row-1,60)
    ws.write_url("B16",SITE,string="Read the case study online")
    ws.write_url("B17",SITE+WORKBOOK,string="Download the model")
    book.close()


def charts(p):
    levels=np.arange(1,p["levels"]+1)
    income=p["income_start"]*p["income_growth"]**(levels-1)
    costs=p["cost_start"]*p["cost_growth"]**(levels-1)
    plt.rcParams.update({"figure.dpi":110,"savefig.bbox":"tight"})
    fig,ax=plt.subplots(figsize=(9,4));ax.plot(levels,income,label="Income / second (soft)");ax.plot(levels,costs,label="Next upgrade (soft)")
    ax.set_yscale('log');ax.set(xlabel="Illustrative level",ylabel="Soft-currency units (different rates/stocks)",title="Reconstructed curves — assumptions, not game telemetry");ax.legend();fig.savefig(ROOT/'charts/01-income-vs-cost.png');plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,4));ax.plot(levels,costs/income,color='#2f6b4f');ax.set(xlabel="Illustrative level",ylabel="Seconds at fixed income",title="Time to afford the next upgrade — static baseline")
    fig.savefig(ROOT/'charts/02-idle-cash-surplus.png');plt.close(fig)
    a=np.array([.25,.35,.45,.55,.65]);b=np.array([.04,.06,.08,.10,.12]);values=p["dau"]*a[:,None]*b[None,:]*p["early_fee"]*p["ingot_retail"]
    fig,ax=plt.subplots(figsize=(8,4));im=ax.imshow(values,cmap='YlGn');ax.set_xticks(range(5),[f'{x:.0%}' for x in b]);ax.set_yticks(range(5),[f'{x:.0%}' for x in a]);ax.set(xlabel="Early-fee spender share among loan users",ylabel="Adoption among DAU",title="Early-fee currency burn — USD retail equivalent/day, not receipts")
    for i in range(5):
        for j in range(5):ax.text(j,i,f'{values[i,j]:,.0f}',ha='center',va='center')
    fig.colorbar(im,ax=ax);fig.savefig(ROOT/'charts/03-loan-sensitivity.png');plt.close(fig)


def documents(p,m):
    values={**{k:str(v) for k,v in p.items()},**{k:str(v) for k,v in m.items()}}
    values.update(**{key+"_pct": f"{p[key]:.1%}" for key in ("adoption", "early_spender_share", "paid_replenishment", "net_realization", "max_reward_ratio", "principal_share", "maturity_interest")})
    values.update(dau_fmt=f'{p["dau"]:,.0f}', after_substitution_pct=f'{1-p["cannibalization"]:.1%}', baseline_cash=f'{p["baseline_arpdau"]:.4f}',
                  cash_10=f'{m["retail"]*.10*p["net_realization"]*(1-p["cannibalization"]):,.2f}',
                  cash_25=f'{m["retail"]*.25*p["net_realization"]*(1-p["cannibalization"]):,.2f}',
                  cash_50=f'{m["retail"]*.50*p["net_realization"]*(1-p["cannibalization"]):,.2f}')
    values.update(loan_cash=f'{m["incremental_cash"]:,.2f}',retail=f'{m["retail"]:,.0f}',ingots=f'{m["ingots"]:,.0f}',
                  ad_base=f'{m["ad_base"]:,.0f}',ad_tuned=f'{m["ad_tuned"]:,.0f}',ad_delta=f'{m["ad_delta"]:,.0f}',
                  annual=f'{m["combined_annual"]:,.0f}',blended=f'{m["blended"]:.4f}',
                  reward_pct=f'{m["reward_ratio"]:.1%}',income=f'{m["income"]:,.0f}',
                  principal=f'{m["principal"]/1e6:,.1f}',benefit=f'{m["total_bonus"]/1e6:,.1f}',
                  max_daily=f'{m["max_daily_bonus_ratio"]:.1%}')
    for template,target in [('case-study.template.html','index.html'),('README.template.md','README.md')]:
        source=(ROOT/template).read_text()
        for key,value in values.items():source=source.replace('{{'+key+'}}',value)
        if '{{' in source:raise ValueError('Unfilled document token in '+template)
        (ROOT/target).write_text(source)
    (ROOT/'docs/model-metrics.json').write_text(json.dumps({'inputs':p,'outputs':m},indent=2)+'\n')


def main():
    p=defaults();m=evaluate(p)
    workbook(p,m);charts(p);documents(p,m)
    print(json.dumps(m,indent=2))


if __name__=='__main__':main()
