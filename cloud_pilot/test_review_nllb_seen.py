"""Synthetic first-attempt/review checks; no inference or semantic ratings."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import uuid

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts import review_nllb_seen as n


def metrics(tokens,value=1.0,batch=1):
    content=tokens-2*batch
    return dict(supervised_tokens=tokens,content_tokens=content,control_tokens=2*batch,tokens_per_control=batch,
        sum_nll=value*tokens,mean_nll=value,native_mean_nll=value,native_absolute_difference=0.0,
        reference_mean_nll=value,reference_absolute_difference=0.0,reference_precision='float32_logits',native_loss_dtype='torch.float32',
        content_sum_nll=value*content,content_mean_nll=value,control_sum_nll=value*2*batch,
        language_tag_sum_nll=value*batch,eos_sum_nll=value*batch)


def fixture():
    token_map=json.loads((n.PACKAGE/'token-map.json').read_bytes())
    rows=token_map['rows']; by_id=n.unique(rows); records=[]
    for call in n.runtime.call_schedule(rows):
        target,source=by_id[call['case_id']],by_id[call['source_parent_id']]
        r=dict(**call,record_id=target['record_id'],work_id=target['work_id'],input_sha256=source['source_sha256'],
            target_sha256=target['target_sha256'],source_record_id=source['record_id'],source_work_id=source['work_id'],
            source_tokens=len(source['input_ids']),target_tokens=len(target['labels']),seconds=0.1)
        if call['kind']=='likelihood': r.update(status='success',**metrics(len(target['labels']),1.0 if call['condition']=='correct' else 2.0))
        else:
            tokens=[2,256053,7,2] if call['sequence']<60 else [2,256053]+[7]*511
            r.update(n.runtime.generation_result(tokens,'synthetic output'))
        records.append(r)
    run=dict(status='completed',completed_call_ids=[r['id'] for r in records],unattempted_call_ids=[],
        completed_likelihood_calls=40,completed_generation_calls=20,generation_failures=1,all_first_attempts_recorded=True)
    checks=[]
    for kind,selected in n.runtime.canary_cases(rows):
        checks.append(dict(kind=kind,parent_ids=[r['id'] for r in selected],scored=False,batch_size=len(selected),
            padded_source_tokens=max(len(r['input_ids']) for r in selected),padded_target_tokens=max(len(r['labels']) for r in selected),
            **metrics(sum(len(r['labels']) for r in selected),batch=len(selected))))
    return token_map,run,records[:40],records[40:],dict(status='passed',checks=checks)


class AnalysisChecks(unittest.TestCase):
    def test_frozen_schedule_arithmetic_caps_and_tampering(self):
        token_map,run,likelihood,predictions,canary=fixture()
        completion=n.validate_records(run,likelihood,predictions,token_map,canary)
        self.assertTrue(completion['all_first_attempts_recorded']); self.assertEqual(completion['generation_failures'],1)
        report=n.likelihood_report(likelihood,token_map)
        self.assertEqual(report['full_target']['overall']['equal_parent_mean'],1.0)
        self.assertEqual(report['content_only']['overall']['signs'],dict(positive=20,zero=0,negative=0))
        rounded=copy.deepcopy(likelihood)
        rounded[0]['native_mean_nll']+=0.002
        rounded[0]['native_absolute_difference']=abs(rounded[0]['native_mean_nll']-rounded[0]['mean_nll'])
        n.validate_records(run,rounded,predictions,token_map,canary)
        for change in ('missing','duplicate','source','target','arithmetic','reference','native_difference'):
            bad=copy.deepcopy(likelihood)
            if change=='missing': bad.pop()
            elif change=='duplicate': bad[1]=copy.deepcopy(bad[0])
            elif change=='source': bad[0]['input_sha256']='wrong'
            elif change=='target': bad[1]['target_sha256']='wrong'
            elif change=='arithmetic': bad[0]['content_sum_nll']+=1
            elif change=='reference':
                bad[0]['reference_mean_nll']+=0.002
                bad[0]['reference_absolute_difference']=abs(bad[0]['reference_mean_nll']-bad[0]['mean_nll'])
            else: bad[0]['native_absolute_difference']+=0.002
            with self.subTest(change=change),self.assertRaises(ValueError):
                n.validate_records(run,bad,predictions,token_map,canary)
        wrong=copy.deepcopy(predictions); wrong[-1]['status']='success'
        with self.assertRaises(ValueError): n.validate_records(run,likelihood,wrong,token_map,canary)
        stopped=dict(run,status='incomplete',completed_call_ids=[],unattempted_call_ids=run['completed_call_ids'],
            completed_likelihood_calls=0,completed_generation_calls=0,generation_failures=0,all_first_attempts_recorded=False,
            error_type='ValueError',error='Native/independent target loss differs')
        missing=n.validate_records(stopped,[],[],token_map,{})
        self.assertFalse(missing['usable_for_translation_review']); self.assertFalse(missing['readiness_passed'])
        self.assertEqual(len(missing['unattempted_call_ids']),60)
        self.assertEqual(n.likelihood_report([],token_map)['status'],'INCOMPLETE_NO_PAIRED_LIKELIHOOD')
        with self.assertRaisesRegex(ValueError,'Incomplete schedule'):
            n.build_files(token_map,[],[],missing,{},None)

    def test_real_qualified_scopes_frozen_packets_and_review_coverage(self):
        token_map,run,likelihood,predictions,canary=fixture()
        completion=n.validate_records(run,likelihood,predictions,token_map,canary)
        material=n.recall.load_material()
        evidence=(token_map,likelihood,predictions,completion,{})
        files=n.build_files(*evidence,material)
        packets={r:n.decode_lines(files[f'reviewer-{r}/packet.jsonl']) for r in n.SEEDS}
        reviews={}
        for reviewer,packet in packets.items():
            self.assertEqual(len(packet),20); self.assertEqual(sum(len(p['scopes']) for p in packet),28)
            self.assertEqual(files[f'reviewer-{reviewer}/INSTRUCTIONS.md'],n.recall.instructions().replace(b'all40',b'all20'))
            reviews[reviewer]=[dict(review_id=p['review_id'],output_sha256=p['output_sha256'],
                judgment='uncertain' if p['execution_status']=='success' else 'not_assessable',
                categories={k:'uncertain' for k in n.recall.CATEGORIES},supported_span_severity='uncertain',
                unknown_span_handling='uncertain',reason='Synthetic schema test, not semantic assessment.',output_span='synthetic',
                local_details=[dict(scope_id=s['scope_id'],status='unassessable',reason='Synthetic scope check.',output_span='') for s in p['scopes']]) for p in packet]
        result=n.summarize(n.decode_lines(files['lead-only/mapping.jsonl']),packets,reviews,completion)
        self.assertEqual(result['reviewers']['A']['denominator'],20)
        self.assertEqual(result['reviewers']['B']['meaning_and_execution_counts'],{'uncertain':19,'error':1})
        for change in ('missing','duplicate','span','scope','failed_merit'):
            bad=copy.deepcopy(reviews['A'])
            if change=='missing': bad.pop()
            elif change=='duplicate': bad[1]=copy.deepcopy(bad[0])
            elif change=='span': bad[0]['output_span']='not in output'
            elif change=='scope': next(r for r in bad if r['local_details'])['local_details'].pop()
            else: next(r for r in bad if r['judgment']=='not_assessable')['judgment']='accepted'
            with self.subTest(change=change),self.assertRaises(ValueError): n.validate_reviews(packets['A'],bad)
        base=ROOT/'resources/local/nllb-seen-analysis-tests'/uuid.uuid4().hex
        base.mkdir(parents=True,exist_ok=False)
        packet_dir=base/'packet'; n.write_fresh(packet_dir,files)
        for reviewer in n.SEEDS: (base/f'{reviewer}.jsonl').write_bytes(n.lines(reviews[reviewer]))
        with patch.object(n,'load_evidence',return_value=evidence):
            n.score(packet_dir,base/'A.jsonl',base/'B.jsonl',base/'scored')
            (packet_dir/'reviewer-A/packet.jsonl').write_bytes(files['reviewer-A/packet.jsonl']+b'\n')
            with self.assertRaisesRegex(ValueError,'Frozen packet'):
                n.score(packet_dir,base/'A.jsonl',base/'B.jsonl',base/'tampered')


if __name__=='__main__': unittest.main()
