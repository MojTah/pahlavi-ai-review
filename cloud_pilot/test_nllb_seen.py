"""Offline tiny-model numerical and persisted-failure checks; no pretrained weights."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.append(str(ROOT/'resources/local/hf-client-venv/Lib/site-packages'))
for name in ('HF_HUB_OFFLINE', 'TRANSFORMERS_OFFLINE', 'HF_HUB_DISABLE_IMPLICIT_TOKEN'):
    os.environ[name] = '1'
from cloud_pilot import nllb_seen as n


@contextmanager
def scratch():
    # Ordinary mkdir avoids Windows sandbox mode700 temporary-directory ACL failures.
    # Retain only tiny generated fixtures; never delete user files or model artifacts.
    folder = ROOT/'resources/local/nllb-seen-tests'/uuid.uuid4().hex
    folder.mkdir(parents=True, exist_ok=False)
    yield folder


class SeenChecks(unittest.TestCase):
    def test_native_manual_shift_padding_controls_and_reload(self):
        import torch
        from transformers import M2M100Config, M2M100ForConditionalGeneration
        from transformers.models.m2m_100.modeling_m2m_100 import shift_tokens_right
        torch.set_num_threads(2)
        torch.manual_seed(3407)
        config = M2M100Config(vocab_size=32, d_model=8, encoder_layers=1, decoder_layers=1,
            encoder_attention_heads=1, decoder_attention_heads=1, encoder_ffn_dim=16, decoder_ffn_dim=16,
            dropout=0.1, attention_dropout=0.1, activation_dropout=0.1, encoder_layerdrop=0.1, decoder_layerdrop=0.1,
            pad_token_id=1, bos_token_id=0, eos_token_id=2, decoder_start_token_id=2)
        config._attn_implementation = 'eager'
        model = M2M100ForConditionalGeneration(config).float().eval().requires_grad_(False)
        rows = [dict(id='short', input_ids=[3, 5, 2], attention_mask=[1,1,1], labels=[4,6,2]),
                dict(id='long', input_ids=[3, 8, 9, 2], attention_mask=[1,1,1,1], labels=[4,7,8,2])]
        labels = torch.tensor([[4,6,2,-100], [4,7,8,2]])
        source = torch.tensor([[3,5,2,1],[3,8,9,2]])
        mask = source != 1
        shifted = shift_tokens_right(labels, 1, 2)
        self.assertEqual(shifted.tolist(), [[2,4,6,2],[2,4,7,8]])
        with torch.inference_mode():
            implicit = model(input_ids=source, attention_mask=mask, labels=labels, use_cache=False)
            explicit = model(input_ids=source, attention_mask=mask, decoder_input_ids=shifted, use_cache=False)
        self.assertTrue(torch.equal(implicit.logits, explicit.logits))
        metrics = n.likelihood_metrics(implicit.logits, labels, implicit.loss, target_tag=4)
        self.assertEqual((metrics['supervised_tokens'],metrics['content_tokens'],metrics['control_tokens']), (7,3,4))
        manual = -torch.log_softmax(implicit.logits.float(), -1)
        self.assertAlmostEqual(metrics['content_sum_nll'], float(manual[0,1,6])+float(manual[1,1,7])+float(manual[1,2,8]), places=6)
        self.assertAlmostEqual(metrics['sum_nll'], metrics['content_sum_nll']+metrics['control_sum_nll'], places=6)
        wrong = implicit.logits.clone()
        wrong[0,3,:] = float('nan')  # ignored padding cannot affect the metric.
        self.assertEqual(metrics, n.likelihood_metrics(wrong, labels, implicit.loss, target_tag=4))
        with patch('torch.nn.functional.cross_entropy', return_value=implicit.loss+0.1):
            with self.assertRaisesRegex(ValueError, 'differs'):
                n.likelihood_metrics(implicit.logits, labels, implicit.loss, target_tag=4)
        bad = labels.clone(); bad[0] = torch.tensor([4,-100,6,2])
        with self.assertRaisesRegex(ValueError, 'padding'):
            n.likelihood_metrics(implicit.logits, bad, implicit.loss, target_tag=4)
        # Exercise the exact forward wrapper in FP32 and BF16 autocast, then actual safetensors reload.
        for autocast in (False, True):
            first = n.forward(model, rows, rows, torch.device('cpu'), autocast=autocast)
            self.assertLessEqual(first['reference_absolute_difference'], 1e-5)
        # Coincident extrema must include a second, shorter parent and run padded inference.
        cases = n.canary_cases(rows)
        self.assertEqual([r['id'] for r in cases[0][1]], ['short'])
        edge = cases[1][1]
        self.assertEqual([r['id'] for r in edge], ['long', 'short'])
        self.assertEqual((max(len(r['input_ids']) for r in edge), max(len(r['labels']) for r in edge)), (4,4))
        self.assertTrue(len(edge[1]['input_ids']) < 4 and len(edge[1]['labels']) < 4)
        padded = n.forward(model, edge, edge, torch.device('cpu'), autocast=False)
        self.assertEqual((padded['supervised_tokens'],padded['content_tokens'],padded['control_tokens']), (7,3,4))
        self.assertAlmostEqual(padded['mean_nll'],metrics['mean_nll'],places=6)
        self.assertAlmostEqual(padded['content_mean_nll'],metrics['content_mean_nll'],places=6)
        self.assertTrue(all(p.grad is None for p in model.parameters()))
        with scratch() as folder:
            model.save_pretrained(folder, safe_serialization=True)
            restored = M2M100ForConditionalGeneration.from_pretrained(folder, local_files_only=True,
                token=False, trust_remote_code=False, dtype=torch.float32, attn_implementation='eager').eval()
            actual = n.forward(restored, rows, rows, torch.device('cpu'), autocast=False)
            self.assertEqual(metrics, actual)

    def test_cuda_bfloat16_native_rounding_uses_explicit_fp32_reference(self):
        import torch
        if not torch.cuda.is_available():
            self.skipTest('Actual CUDA required for this regression; CPU cannot certify it')
        torch.manual_seed(3407)
        for vocab in (32,256215):
            logits=(torch.randn((2,6,vocab),device='cuda')*8).bfloat16()
            labels=torch.tensor([[4,8,9,10,11,2],[4,7,2,-100,-100,-100]],device='cuda')
            with torch.autocast('cuda',dtype=torch.bfloat16):
                raw=torch.nn.functional.cross_entropy(logits.reshape(-1,vocab),labels.reshape(-1))
            actual=n.likelihood_metrics(logits,labels,raw,target_tag=4)
            self.assertLessEqual(actual['reference_absolute_difference'],1e-5)
            self.assertEqual(actual['native_mean_nll'],float(raw))
            self.assertEqual(actual['native_loss_dtype'],str(raw.dtype))
            self.assertEqual(actual['native_absolute_difference'],abs(float(raw)-actual['mean_nll']))
            self.assertEqual((actual['supervised_tokens'],actual['content_tokens'],actual['control_tokens']),(9,5,4))
            ref64=-torch.log_softmax(logits.double(),-1).gather(-1,labels.clamp_min(0).unsqueeze(-1)).squeeze(-1)
            self.assertAlmostEqual(actual['mean_nll'],float(ref64[labels!=-100].mean()),places=5)
        # Exercise the actual model-forward wrapper on this host GPU as well.
        from transformers import M2M100Config,M2M100ForConditionalGeneration
        config=M2M100Config(vocab_size=32,d_model=8,encoder_layers=1,decoder_layers=1,
            encoder_attention_heads=1,decoder_attention_heads=1,encoder_ffn_dim=16,decoder_ffn_dim=16,
            pad_token_id=1,eos_token_id=2,decoder_start_token_id=2)
        config._attn_implementation='eager'
        model=M2M100ForConditionalGeneration(config).float().cuda().eval().requires_grad_(False)
        rows=[dict(input_ids=[3,5,2],attention_mask=[1,1,1],labels=[4,6,2]),
              dict(input_ids=[3,8,9,2],attention_mask=[1,1,1,1],labels=[4,7,8,2])]
        result=n.forward(model,rows,rows,torch.device('cuda'))
        self.assertLessEqual(result['reference_absolute_difference'],1e-5)

    @patch.object(n.frozen, 'emit')
    def test_exact_order_persisted_partial_failure_and_caps(self, _emit):
        rows = [dict(id='p'+str(i), record_id='r'+str(i), work_id='w'+str(i), source_sha256='s'+str(i),
            target_sha256='t'+str(i), mismatched_source_parent_id='p'+str((i+5)%20)) for i in range(20)]
        schedule = n.call_schedule(rows)
        self.assertEqual(len(schedule),60)
        self.assertEqual([r['id'] for r in schedule[:4]], ['p0:correct','p0:mismatched','p1:mismatched','p1:correct'])
        self.assertTrue(all(r['kind']=='likelihood' for r in schedule[:40]))
        self.assertEqual([r['case_id'] for r in schedule[40:]], [r['id'] for r in rows])
        success = n.generation_result([2,256053,7,2], 'x')
        self.assertEqual(success['status'],'success')
        self.assertEqual(n.generation_result([2,256053,7,2], ' ')['status'],'failed')
        self.assertEqual(n.generation_result([2,256053]+[7]*510+[2], 'x')['status'],'failed')
        self.assertEqual(n.generation_result([2,256053,7], 'x')['status'],'failed')
        with scratch() as folder:
            output = Path(folder); state = {}
            count = [0]
            def fault(parent, source):
                count[0] += 1
                if count[0] == 3: raise FloatingPointError('injected numerical failure')
                return dict(mean_nll=1.0)
            with self.assertRaisesRegex(RuntimeError, 'stopped'):
                n.execute(rows, output, state, time.monotonic()+30, fault, lambda s: success)
            actual = n.lines(output/'likelihood.jsonl')
            self.assertEqual(len(actual),3)
            self.assertEqual(actual[-1]['status'],'failed')
            self.assertEqual(actual[-1]['error_type'],'FloatingPointError')
            saved = json.loads((output/'run.json').read_text())
            self.assertEqual(saved['status'],'incomplete')
            self.assertEqual(len(saved['unattempted_call_ids']),57)
            self.assertFalse((output/'predictions.jsonl').exists())
        with scratch() as folder:
            state = {}
            n.execute(rows, folder, state, time.monotonic()+30, lambda a,b: dict(mean_nll=1.0),
                lambda s: n.generation_result([2,256053]+[7]*511, 'retained capped output'))
            self.assertEqual(state['status'],'completed')
            self.assertEqual(len(n.lines(Path(folder)/'predictions.jsonl')),20)
            self.assertFalse(state['unattempted_call_ids'])
            self.assertTrue(state['all_first_attempts_recorded'])
            self.assertEqual((state['completed_likelihood_calls'],state['completed_generation_calls'],state['generation_failures']), (40,20,20))
        with scratch() as folder:
            state = {}
            def generation_error(source):
                raise RuntimeError('injected generation failure')
            with self.assertRaisesRegex(RuntimeError, 'stopped'):
                n.execute(rows, folder, state, time.monotonic()+30, lambda a,b: dict(mean_nll=1.0), generation_error)
            self.assertEqual(len(n.lines(folder/'likelihood.jsonl')),40)
            self.assertEqual(len(n.lines(folder/'predictions.jsonl')),1)
            self.assertEqual(len(state['unattempted_call_ids']),19)
            self.assertFalse(state['all_first_attempts_recorded'])
        with scratch() as folder:
            state = {}
            with self.assertRaises(TimeoutError):
                n.execute(rows, folder, state, time.monotonic()-1, lambda a,b: {}, lambda s: success)
            self.assertEqual(len(state['unattempted_call_ids']),60)


if __name__ == '__main__': unittest.main()
