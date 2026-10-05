"""Describe judgment drift on identical cached DEV15 outputs; preserve old records."""
from collections import Counter
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
import review
from scripts import prepare_blind_dev_assisted as prep

def history():
    records=[];pins={}
    def load(path,json_document=False):
        raw=(review.ROOT/path).read_bytes();pins[path]=prep.sha(raw)
        return json.loads(raw) if json_document else prep.decode_lines(raw)
    for r in load(review.DEV+'/reviews.jsonl'):
        if r['case_id'] in review.IDS:
            records.append({'panel':'original','reviewer':r['reviewer_id'],'arm':'original_'+r['condition'],
                'case_id':r['case_id'],'output_sha256':r['output_sha256'],'judgment':r['judgment']})
    for panel,base,aliases in [
        ('assisted','experiments/dev-assisted-qualified-20260927/blind-comparison',{'gemma280_plain':'step280_plain','gemma280_assisted':'step280_assisted'}),
        ('corrected','experiments/corrected-review-20260930',{'gemma280_plain':'step280_plain','mixed96_plain':'mixed96','corrected96_plain':'corrected96'})]:
        maps=load(base+'/lead-only/mapping.jsonl')
        for rater in ('A','B'):
            ratings=prep.unique(load(base+'/reviewer-'+rater+'/reviews.jsonl'),'review_id')
            for m in maps:
                if m['reviewer']==rater and m['case_id'] in review.IDS and m['condition'] in aliases:
                    r=ratings[m['review_id']]
                    prep.require(r['output_sha256']==m['output_sha256'],'Historical mapping hash differs')
                    records.append({'panel':panel,'reviewer':rater,'arm':aliases[m['condition']],
                        'case_id':m['case_id'],'output_sha256':m['output_sha256'],'judgment':r['judgment']})
    base='experiments/dose-acquisition-20260930/live-execution'
    mapping=load(base+'/blind-mapping.json',True)
    for rater in ('a','b'):
        for r in load(base+'/reviewer-'+rater+'.jsonl'):
            m=mapping[r['blind_id']]
            if m['case_id'] in review.IDS and m['arm'] in ('reference','dose384'):
                records.append({'panel':'dose','reviewer':rater.upper(),
                    'arm':'dose_baseline_nf4' if m['arm']=='reference' else 'dose384_nf4',
                    'case_id':m['case_id'],'output_sha256':m['output_sha256'],'judgment':r['label']})
    return records,pins

def main():
    result,spans=review.summarize(review.OUT)
    historical,pins=history()
    members=prep.decode_lines((review.OUT/'lead-only/members.jsonl').read_bytes())
    index={(m['arm'],m['case_id']):m for m in members}
    mapping=prep.decode_lines((review.OUT/'lead-only/mapping.jsonl').read_bytes())
    by_reviewer={}
    for rater in ('A','B'):
        ratings=prep.unique(prep.decode_lines((review.OUT/f'reviewer-{rater}/reviews.jsonl').read_bytes()),'review_id')
        by_reviewer[rater]={m['context_output_sha256']:ratings[m['review_id']] for m in mapping if m['reviewer']==rater}
    changes=[]
    for old in historical:
        member=index[(old['arm'],old['case_id'])]
        prep.require(member['output_sha256']==old['output_sha256'],'Historical output is not identical')
        for rater in ('A','B'):
            new=by_reviewer[rater][member['context_output_sha256']]
            changes.append({**old,'new_reviewer':rater,'new_judgment':new['judgment'],
                'changed':old['judgment']!=new['judgment'],'comparison':'judgment drift on identical source/output; raters/panels not interchangeable'})
    old_counts=[]
    for panel,rater,arm in sorted({(r['panel'],r['reviewer'],r['arm']) for r in historical}):
        selected=[r for r in historical if (r['panel'],r['reviewer'],r['arm'])==(panel,rater,arm)]
        old_counts.append({'panel':panel,'reviewer':rater,'arm':arm,'denominator':len(selected),'counts':dict(Counter(r['judgment'] for r in selected))})
    drift={'historical_source_pins':pins,'historical_memberships':len(historical),
        'comparisons':len(changes),'changed_comparisons':sum(x['changed'] for x in changes),
        'old_counts':old_counts,'new_counts':result['reviewers'],
        'warning':'Comparisons count each historical label against both new raters; not independent observations or a temporal improvement measure.'}
    # Representative IDs fixed before inspecting the reassessment responses:
    # one per DEV work, not a random sample or an accuracy endpoint.
    fixed=('QUALITYDEV1-002','QUALITYDEV1-007','QUALITYDEV1-013','QUALITYDEV1-020')
    by_case={cid:[m for m in members if m['case_id']==cid] for cid in review.IDS}
    disagreements={r['context_output_sha256'] for r in result['unique_output_disagreements']}
    extra=[]
    for cid in review.IDS:
        for m in sorted(by_case[cid],key=lambda m:m['arm']):
            if m['context_output_sha256'] in disagreements:
                extra.append(m)
                break
        if len(extra)==4:break
    chosen=[next(m for m in by_case[cid] if m['arm']=='step280_plain') for cid in fixed]
    packet=prep.unique(prep.decode_lines((review.OUT/'reviewer-A/packet.jsonl').read_bytes()),'review_id')
    context_ids={m['context_output_sha256']:m['review_id'] for m in mapping if m['reviewer']=='A'}
    def item(m,kind):
        match=packet[context_ids[m['context_output_sha256']]]
        return {'kind':kind,'case_id':m['case_id'],'work_id':m['work_id'],'arm':m['arm'],'context_output_sha256':m['context_output_sha256'],
            'evidence':match,'review_A':by_reviewer['A'][m['context_output_sha256']],'review_B':by_reviewer['B'][m['context_output_sha256']]}
    calibration={'status':'FOR_EVENTUAL_QUALIFIED_REVIEW_NO_CONTACT','representative_ids_fixed_before_unblinding':fixed,
        'disagreement_selection':'first differing output in sorted arm order for up to first4case IDs; separately labeled, not representative',
        'expert_adjudicated':False,'records':[item(m,'prespecified_one_per_work') for m in chosen]+[item(m,'disagreement_example') for m in extra]}
    for name,data in {'summary.json':prep.json_bytes(result),'span-offsets.jsonl':prep.lines(spans),
                      'historical-drift.json':prep.json_bytes(drift),'historical-label-comparisons.jsonl':prep.lines(changes),
                      'calibration.json':prep.json_bytes(calibration)}.items():
        (review.OUT/name).write_bytes(data)
    print(json.dumps({'historical_memberships':len(historical),'changed_comparisons':drift['changed_comparisons'],
        'all_label_comparisons':len(changes),'unique_output_disagreements':len(disagreements),'calibration_records':len(calibration['records'])}))

if __name__=='__main__':main()
