"""Checks actual reviewed cases and boundaries; no models or paid operations."""
from copy import deepcopy
import json
import unittest
import prepare as p


class PreparationChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows={r['id']:r for r in p.bundle.jsonl(p.READER.read_bytes())}
        cls.decisions={r['id']:r for r in json.loads((p.HERE/'target-decisions.json').read_text('utf8'))['decisions']}

    def test_lexical_plain_target_language_and_scope(self):
        row=next(r for r in self.rows.values() if r['task']=='lexical-en' and r['learning']['source']==['ābādānīh'])
        prompt,answer=p.prompt_answer(row)
        self.assertEqual(answer,'prosperity, cultivation')
        self.assertIn('Use plain text',prompt)
        self.assertIn('meanings in English',prompt)
        self.assertIn(p.js(row['learning']['context']),prompt)
        malformed=deepcopy(row);malformed['learning']['target']={'entries':[]}
        with self.assertRaises(ValueError):
            p.prompt_answer(malformed)

    def test_abus_spacing_and_qualifier(self):
        rid='kosh:cpd:70742f1be12f3b749b47752fa5229fbd52107e29:block:0'
        row=p.apply_decision(self.rows[rid],self.decisions[rid])
        self.assertEqual(row['learning']['target'],'(woman) having just given birth')
        self.assertEqual(row['learning']['source'],['abus'])
        self.assertEqual(self.rows[rid]['learning']['target'],'(woman)havingjust given birth')

    def test_material_brackets_and_populated_glosses_survive(self):
        for code,required in [('137001023','[اهریمن]'),('137001028','[و]'),('301007008','{اساس و حاصل}')]:
            rid='parsig:'+code+':pal>fa'
            row=p.apply_decision(self.rows[rid],self.decisions[rid])
            self.assertIn(required,row['learning']['target'])
        rid='parsig:136003017:pal>fa'
        row=p.apply_decision(self.rows[rid],self.decisions[rid])
        self.assertTrue(row['learning']['target'].endswith('.'))
        self.assertIn('به (= بلکه)',row['learning']['target'])
        self.assertIn('کسته (= ناحیه، سوی)',row['learning']['target'])

    def test_annotated_fragments_need_explicit_context(self):
        for rid in ['openampd:MP5650:full','openampd:MP0437:full','openampd:MP0093:full']:
            row=p.apply_decision(self.rows[rid],self.decisions[rid])
            self.assertEqual(row['learning'],self.rows[rid]['learning'])
            prompt,_=p.prompt_answer(row)
            self.assertIn('Preserve damage, uncertainty, editorial additions',prompt)
            bad=deepcopy(self.rows[rid]);bad['learning']['context']['evidence_class']='COMPLETE_PROSE'
            with self.assertRaises(ValueError):
                p.apply_decision(bad,self.decisions[rid])

    def test_cross_record_holds_and_changed_input(self):
        for code in ['151000045','151000046']:
            rid='parsig:'+code+':pal>fa'
            self.assertIsNone(p.apply_decision(self.rows[rid],self.decisions[rid]))
        rid='parsig:134009019:pal>fa'
        bad=deepcopy(self.rows[rid]);bad['learning']['target']+=' invented word'
        with self.assertRaises(ValueError):
            p.apply_decision(bad,self.decisions[rid])
        bad=deepcopy(self.rows[rid]);bad['learning']['source']+=' nē'
        with self.assertRaises(ValueError):
            p.apply_decision(bad,self.decisions[rid])


if __name__=='__main__':
    unittest.main()
