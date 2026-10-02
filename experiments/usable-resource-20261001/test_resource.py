"""Bounded meaning/scope regression checks; no cloud or weights."""
from copy import deepcopy
import unittest

import prepare as p


class ResourceChecks(unittest.TestCase):
    def test_plain_gloss_and_unknown_fields(self):
        target={'entries':[{'senses':[{'number_as_published':None,'components':[
            {'attributes':{},'kind':'tr','text':'prosperity, cultivation'}]}]}]}
        text,mapping,_=p.render(target,'lexical-en')
        self.assertEqual(text,'prosperity, cultivation')
        self.assertEqual(len(mapping),1)
        broken=deepcopy(target)
        broken['entries'][0]['unhandled_qualification']='uncertain'
        with self.assertRaises(ValueError):
            p.render(broken,'lexical-en')

    def test_senses_forms_and_relation_direction(self):
        target={'entries':[{'senses':[{'number_as_published':'1','text':'آفریدن'},
                                    {'number_as_published':'2','text':'مقدر کردن'}],
            'related_forms':[{'forms':['brēhēnīd'],'senses':'آفرید'},
                             {'forms':['brēhēnīhist'],'senses':'آفریده شد'}]},
            {'senses':'اُفتاد.','related_forms':[{'forms':['ōpastan'],
              'headword_relation_to_this_form_as_published':'بن ماضی از',
              'qualification_as_published':'شیرازی کُهن'}]}]}
        text,_,_=p.render(target,'lexical-fa')
        self.assertIn('Entry 1:\n1. آفریدن\n2. مقدر کردن',text)
        self.assertIn('Related form: brēhēnīd — آفرید',text)
        self.assertIn('Related form: brēhēnīhist — آفریده شد',text)
        self.assertIn('Related form: ōpastan; headword relation to this form: بن ماضی از; qualification: شیرازی کُهن',text)
        compound={'entries':[{'sense_type':'compound_components_as_published','components':[
            {'forms':['u'],'senses':'و'},{'forms':['š-'],'senses':'ش'}]}]}
        self.assertEqual(p.render(compound,'lexical-fa')[0],'Compound components:\nu — و\nš- — ش')

    def test_safe_quotes_and_uncertainty(self):
        target={'entries':[{'senses':"`also, too'."}]}
        text,mappings,_=p.render(target,'lexical-mmp-en')
        self.assertEqual(text,'also, too.')
        self.assertEqual(mappings[0]['operation'],'whole_gloss_quote_delimiters_removed')
        for value in ["`also' or `too'.",'offspring (?)','[unclear] child','final(ly)','rise (sun)']:
            target['entries'][0]['senses']=value
            self.assertEqual(p.render(target,'lexical-mmp-en')[0],value)

    def test_exact_qualification_whitelist(self):
        decision=next(v for v in p.punctuation_decisions().values() if v['text']=='(with a negative)' and v['kind']=='usg')
        target={'entries':[{'senses':[{'number_as_published':None,'components':[
            {'attributes':{},'kind':'usg','text':'(with a negative)'},
            {'attributes':{},'kind':'tr','text':'ever'}]}]}]}
        text,_,_=p.render(target,'lexical-en',decision['id'])
        self.assertEqual(text,'Usage: with a negative; Meaning: ever')
        # Identical typography at a different locus has no reviewed removal.
        self.assertEqual(p.render(target,'lexical-en','not-reviewed')[0],'Usage: (with a negative); Meaning: ever')
        target['entries'][0]['senses'][0]['components'][0]['text']='(with a positive)'
        with self.assertRaises(ValueError):
            p.render(target,'lexical-en',decision['id'])

    def test_reviewed_abbreviation_has_one_terminal_period(self):
        records=p.rows((p.PARENT/'learning-projections.jsonl').read_bytes())
        by_id={r['id']:r for r in records}
        decisions=[d for d in p.punctuation_decisions().values() if d['text'] in {'(tr.).','(intr.).'}]
        self.assertEqual(len(decisions),8)
        for d in decisions:
            text,mapping,_=p.render(by_id[d['id']]['learning']['target'],'lexical-en',d['id'])
            self.assertNotIn('tr..',text)
            self.assertIn('reviewed_whole_parenthesis_and_redundant_terminal_period_removed',
                          [m['operation'] for m in mapping])


if __name__=='__main__':
    unittest.main()
