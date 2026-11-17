"""Check arithmetic, formula caches, PDF links and optional real recalculation."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import tempfile
import openpyxl
from pypdf import PdfReader
from model import ROOT, INPUTS, defaults, evaluate

WORKBOOK='Idle_Bank_Tycoon_Economy_Model.xlsx'
CELLS={'Loan Desk (A)':{'C6':'level','C7':'income','C9':'principal','C14':'total_bonus',
                       'C15':'reward_ratio','C16':'guardrail','C17':'max_daily_loans',
                       'C18':'max_daily_bonus_ratio','C19':'slot_status','C22':'ingots',
                       'C23':'retail','C24':'incremental_cash','C25':'cash_arpdau'},
       'Ad Tuning (B)':{'C7':'ad_base','C8':'ad_tuned','C9':'ad_delta',
                        'C12':'instant_ad_reward','C13':'ad_boost_reward'},
       'KPI Impact':{'C9':'combined_daily','C10':'combined_annual','C11':'blended'}}


def check_calculated(path,parameters):
    values=openpyxl.load_workbook(path,data_only=True)
    expected=evaluate(parameters)
    for sheet,mapping in CELLS.items():
        for cell,key in mapping.items():
            actual=values[sheet][cell].value; target=expected[key]
            same=actual==target if isinstance(target,str) else actual is not None and math.isclose(actual,target,rel_tol=1e-9,abs_tol=1e-9)
            assert same,(sheet,cell,actual,target)
    for ws in values:
        assert not [(c.coordinate,c.value) for row in ws for c in row if c.data_type=='e'],ws.title
    for row,share in enumerate((0,.10,.25,.50),15):
        cash=expected['retail']*share*parameters['net_realization']*(1-parameters['cannibalization'])
        assert math.isclose(values['KPI Impact'][f'D{row}'].value,cash,abs_tol=1e-8)
    return values


def recalculate():
    executable=shutil.which('soffice') or shutil.which('libreoffice')
    if not executable:raise RuntimeError('LibreOffice is required for --recalculate')
    changes=[{}, {'loan_multiplier':1.5}, {'paid_replenishment':0},
             {'extra_buyer_share':.02,'extra_slot_price':60,'free_slots':2},
             {'levels':10,'example_level':30,'loan_hours':8,'free_slots':3,'extra_buyer_share':.02},
             {'tuned_views':5,'reward_minutes':45,'ad_boost_hours':3,'maturity_interest':.05}]
    with tempfile.TemporaryDirectory(prefix='idle-recalculation-') as tmp:
        tmp=Path(tmp);source=tmp/'inputs';out=tmp/'outputs';source.mkdir();out.mkdir()
        for index,change in enumerate(changes):
            book=openpyxl.load_workbook(ROOT/WORKBOOK)
            for row,(key,*_) in enumerate(INPUTS,6):
                if key in change:book['Parameters'][f'C{row}']=change[key]
            book.save(source/f'scenario-{index}.xlsx')
        command=[executable,'--headless',f'-env:UserInstallation={(tmp/"profile").as_uri()}',
                 '--convert-to','xlsx','--outdir',str(out),*[str(p) for p in sorted(source.glob('*.xlsx'))]]
        result=subprocess.run(command,capture_output=True,text=True,timeout=120)
        if result.returncode:raise RuntimeError(result.stdout+result.stderr)
        for index,change in enumerate(changes):
            params={**defaults(),**change};calculated=out/f'scenario-{index}.xlsx'
            assert calculated.exists(),result.stdout+result.stderr
            book=check_calculated(calculated,params)
            active=[book['Baseline Economy'][f'C{row}'].value for row in range(6,126)]
            assert sum(v not in (None,'') for v in active)==params['levels']
        print('PASS LibreOffice: six real recalculation scenarios, cash zero, reward breach, slots, level horizon and ad downside')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--recalculate',action='store_true');args=parser.parse_args()
    params=defaults();m=evaluate(params);check_calculated(ROOT/WORKBOOK,params)
    assert evaluate({**params,'paid_replenishment':0})['incremental_cash']==0
    reference={**params,'loan_hours':4,'offline_hours':12,'principal_share':.4,'maturity_interest':.1,'max_reward_ratio':.5}
    assert evaluate({**reference,'loan_multiplier':1.5})['guardrail']=='BREACH'
    assert math.isclose(evaluate({**reference,'loan_multiplier':1.35})['reward_ratio'],.47)
    assert m['incremental_cash'] <= m['retail']
    formulas=openpyxl.load_workbook(ROOT/WORKBOOK,data_only=False)
    assert all(formulas['Parameters'][f'C{row}'].value==params[key] for row,(key,*_) in enumerate(INPUTS,6))
    strings=[c.value for ws in formulas for row in ws for c in row if c.data_type=='f']
    for row,(key,*_) in enumerate(INPUTS,6):
        assert any(f'Parameters!$C${row}' in f for f in strings),key
    assert len(formulas['Parameters'].data_validations.dataValidation)==len(INPUTS)
    pdf=PdfReader(ROOT/'docs/case-study.pdf');text=' '.join(page.extract_text() or '' for page in pdf.pages)
    assert f'{m["reward_ratio"]:.1%}' in text and f'{m["incremental_cash"]:,.2f}' in text and f'{m["retail"]:,.0f}' in text
    assert 'drains more currency than it grants' not in text
    links=[a.get_object().get('/A',{}).get('/URI','') for page in pdf.pages for a in page.get('/Annots',[])]
    assert any(WORKBOOK in link for link in links),links
    manifest=json.loads((ROOT/'docs/build-manifest.json').read_text())
    for path,digest in manifest.items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    print(f'PASS defaults and {len(strings)} formula caches; all inputs referenced/validated; {len(pdf.pages)}-page PDF has model links and fresh hashes')
    if args.recalculate:recalculate()


if __name__=='__main__':main()
