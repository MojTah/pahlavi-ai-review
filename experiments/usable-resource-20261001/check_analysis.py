"""Verify the partial preparation's identities and spans, not linguistic truth."""
import json
import prepare as p


def check():
    report=json.loads((p.HERE/'analysis-candidates.json').read_text('utf8'))
    for name,pin in report['source_inputs_sha256'].items():
        if p.sha((p.ROOT/name).read_bytes())!=pin:
            raise ValueError('Changed analysis input: '+name)
    view=report['local_view']
    raw=(p.ROOT/view['path']).read_bytes()
    if p.sha(raw)!=view['sha256'] or len(raw)!=view['bytes']:
        raise ValueError('Changed analysis view')
    views=p.rows(raw)
    cases=report['source_analysis_cases']
    assert len(cases)==len(views)==view['rows']==15
    assert len({c['id'] for c in cases})==15
    assert len({c['work_family'] for c in cases})==1
    assert report['complete_pilot_cases']==0 and not report['paid_launch_allowed']
    qualified={r['id'] for r in p.rows((p.PARENT/'learning-projections.jsonl').read_bytes())}
    selected={r['id'] for r in p.rows((p.PARENT/'train.jsonl').read_bytes())}
    for case,local in zip(cases,views):
        assert {k:v for k,v in local.items() if k!='source'}==case
        source={r['id']:r for r in p.rows((p.ROOT/case['source_file']).read_bytes())}[case['id']]
        projection={k:source[k] for k in ['id','pahlavi_transcription','source_pdf','source_pdf_sha256','pdf_page_1_based','printed_page']}
        assert p.sha(p.canonical(projection).encode('utf8'))==case['source_projection_sha256']
        text=source['pahlavi_transcription']
        assert local['source']==text and case['full_source_span']==[0,len(text)]
        for binding in case['span_bindings']:
            a,b=binding['source_span']
            assert 0<=a<b<=len(text)
            assert p.sha(text[a:b].encode('utf8'))==binding['source_text_sha256']
        assert case['in_current_qualified_pool']==(case['id'] in qualified)
        assert case['in_previous_selected1536']==(case['id'] in selected)
        assert not case['target_used_to_derive_analysis'] and not case['candidate_outputs_used']
    count=sum(case['in_previous_selected1536'] for case in cases)
    assert count==14
    print(f'PASS:15 bound construction candidates,1 lineage,{count} previously selected;0 complete pilot cases. No linguistic or launch certification.')


if __name__=='__main__':
    check()
