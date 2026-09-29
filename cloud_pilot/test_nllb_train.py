"""Offline checks of the NEW schedule, pooled loss, and exact state resume; no pretrained weights."""
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import uuid
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.append(str(ROOT / 'resources/local/hf-client-venv/Lib/site-packages'))
for key in ('HF_HUB_OFFLINE', 'TRANSFORMERS_OFFLINE', 'HF_HUB_DISABLE_IMPLICIT_TOKEN'):
    os.environ[key] = '1'
from cloud_pilot import nllb_train as n


class NllbChecks(unittest.TestCase):
    def test_schedule_complete_deterministic(self):
        groups = n.schedule()
        self.assertEqual(groups, n.schedule())
        self.assertEqual(len(groups), 700)
        self.assertEqual(sum(map(len, groups)), 11185)
        for epoch in range(5):
            self.assertEqual(sorted(i for group in groups[epoch*140:(epoch+1)*140] for i in group), list(range(2237)))
            self.assertEqual(len(groups[(epoch+1)*140-1]), 13)
        self.assertEqual(n.rate(42), 3e-5)
        self.assertEqual(n.rate(700), 0)
        with self.assertRaises(ValueError): n.schedule(2236)

    def test_pooled_update_and_exact_resume(self):
        import torch
        import torch.nn.functional as F
        from transformers import M2M100Config, M2M100ForConditionalGeneration
        torch.set_num_threads(2)
        torch.manual_seed(77)
        config = M2M100Config(vocab_size=32, d_model=8, encoder_layers=1, decoder_layers=1,
            encoder_attention_heads=1, decoder_attention_heads=1, encoder_ffn_dim=16, decoder_ffn_dim=16,
            dropout=0, attention_dropout=0, activation_dropout=0, encoder_layerdrop=0, decoder_layerdrop=0,
            pad_token_id=1, bos_token_id=0, eos_token_id=2, decoder_start_token_id=2)
        config._attn_implementation = 'eager'
        model = M2M100ForConditionalGeneration(config).float()
        reference = copy.deepcopy(model)
        def collate(rows):
            source_max=max(len(r['input_ids']) for r in rows)
            target_max=max(len(r['labels']) for r in rows)
            return {'input_ids':torch.tensor([r['input_ids']+[1]*(source_max-len(r['input_ids'])) for r in rows]),
                'attention_mask':torch.tensor([[1]*len(r['input_ids'])+[0]*(source_max-len(r['input_ids'])) for r in rows]),
                'labels':torch.tensor([r['labels']+[-100]*(target_max-len(r['labels'])) for r in rows])}
        rows=[{'input_ids':[3,5,2], 'labels':[4]+[6]*(i+1)+[2]} for i in range(7)]
        optimizer=n.optimizer_for(model)
        ref_optimizer=n.optimizer_for(reference)
        metrics=n.update(model,optimizer,rows,collate,1,torch.device('cpu'),autocast=False)
        batch=collate(rows)
        response=reference(**batch,use_cache=False)
        loss=F.cross_entropy(response.logits.reshape(-1,32),batch['labels'].reshape(-1),ignore_index=-100,reduction='sum')/sum(len(r['labels']) for r in rows)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(reference.parameters(),1.0,error_if_nonfinite=True)
        for group in ref_optimizer.param_groups: group['lr']=n.rate(1)
        ref_optimizer.step()
        for a,b in zip(model.parameters(),reference.parameters()):
            self.assertTrue(torch.allclose(a,b,atol=2e-7,rtol=1e-5))
        self.assertAlmostEqual(metrics['loss'],loss.item(),places=5)
        class DummyTokenizer:
            def save_pretrained(self, folder):
                (folder/'tokenizer-test.json').write_text('{}')
        base=ROOT/'resources/local/nllb-tests'
        base.mkdir(exist_ok=True)
        # Keep bounded random test artifacts; this is not a pretrained model download.
        folder=base/('state-'+uuid.uuid4().hex)/'model'
        n.save_state(model,DummyTokenizer(),optimizer,folder,1,'test-order')
        reloaded,resumed=n.reload_state(folder,torch.device('cpu'),1,'test-order')
        for a,b in zip(model.parameters(),reloaded.parameters()):
            self.assertTrue(torch.equal(a,b), 'Reload altered parameter bytes before continuation')
        n.update(model,optimizer,rows,collate,2,torch.device('cpu'),autocast=False)
        n.update(reloaded,resumed,rows,collate,2,torch.device('cpu'),autocast=False)
        for (name,a),(_,b) in zip(model.named_parameters(),reloaded.named_parameters()):
            self.assertTrue(torch.equal(a,b), (name,float((a-b).detach().abs().max())))
        # Exercise nonzero dropout and layerdrop with both branches starting from saved RNG.
        config.dropout=0.1
        config.encoder_layerdrop=0.1
        config.decoder_layerdrop=0.1
        stochastic=M2M100ForConditionalGeneration(config).float()
        stochastic_optimizer=n.optimizer_for(stochastic)
        n.update(stochastic,stochastic_optimizer,rows,collate,1,torch.device('cpu'),autocast=False)
        checkpoint=base/('rng-'+uuid.uuid4().hex)/'model'
        n.save_state(stochastic,DummyTokenizer(),stochastic_optimizer,checkpoint,1,'rng-order')
        n.update(stochastic,stochastic_optimizer,rows,collate,2,torch.device('cpu'),autocast=False)
        recovered,recovered_optimizer=n.reload_state(checkpoint,torch.device('cpu'),1,'rng-order')
        n.update(recovered,recovered_optimizer,rows,collate,2,torch.device('cpu'),autocast=False)
        for a,b in zip(stochastic.parameters(),recovered.parameters()):
            self.assertTrue(torch.equal(a,b),'Nonzero dropout resume changed parameters')


if __name__ == '__main__': unittest.main()
