"""Offline CPU numerical check: native Trainer parent vs token normalization."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
HERE.mkdir(parents=True, exist_ok=True)
for name in ('tmp', 'hf-cache', 'torch-cache'):
    (HERE / name).mkdir(exist_ok=True)
os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1',
                  HF_HUB_DISABLE_TELEMETRY='1', WANDB_DISABLED='true',
                  HF_HOME=str(HERE / 'hf-cache'), TORCH_HOME=str(HERE / 'torch-cache'),
                  TEMP=str(HERE / 'tmp'), TMP=str(HERE / 'tmp'))
sys.path.extend([str(ROOT / 'resources/local/train-fit-deps'),
                 str(ROOT / 'resources/local/hf-client-venv/Lib/site-packages')])

import copy
import hashlib
import inspect
import json
import platform
import tempfile
import torch
import torch.nn.functional as F
import transformers
import peft
import accelerate
from transformers import Gemma4Config, Gemma4TextConfig, Gemma4ForConditionalGeneration
from transformers import Trainer, TrainingArguments, TrainerCallback
from peft import LoraConfig, get_peft_model

tempfile.tempdir = str(HERE / 'tmp')
torch.set_num_threads(1)
torch.manual_seed(3407)
torch.use_deterministic_algorithms(True)
assert transformers.__version__ == '5.13.1'
config = Gemma4Config(text_config=Gemma4TextConfig(
    vocab_size=32, hidden_size=32, intermediate_size=48, num_hidden_layers=2,
    num_attention_heads=4, num_key_value_heads=2, head_dim=8, global_head_dim=8,
    max_position_embeddings=64, vocab_size_per_layer_input=32,
    hidden_size_per_layer_input=0, layer_types=['sliding_attention', 'full_attention'],
    sliding_window=16, final_logit_softcapping=30.0, attention_dropout=0.0),
    vision_config=None, audio_config=None)
config._attn_implementation = 'eager'
initial = get_peft_model(Gemma4ForConditionalGeneration(config), LoraConfig(
    r=2, lora_alpha=4, target_modules=['q_proj', 'v_proj'],
    lora_dropout=0.0, task_type='CAUSAL_LM', bias='none'))
initial.config.use_cache = False
initial.config.text_config.use_cache = False
with torch.no_grad():
    for name, parameter in initial.named_parameters():
        if 'lora_B' in name:
            parameter.normal_(0.0, 0.2)
assert all('lora_' in n for n, p in initial.named_parameters() if p.requires_grad)

examples = [
    {'input_ids': [2, 3, 4, 7, 1], 'attention_mask': [1] * 5,
     'labels': [-100, -100, -100, 7, 1]},
    {'input_ids': [2, 11, 12, 13, 14, 15, 16, 1], 'attention_mask': [1] * 8,
     'labels': [-100, -100, -100, 13, 14, 15, 16, 1]},
]

def collate(batch):
    assert len(batch) == 1
    return {k: torch.tensor([batch[0][k]], dtype=torch.long) for k in batch[0]}

def trainable(model):
    return {n: p for n, p in model.named_parameters() if p.requires_grad}

def optimizer(model):
    return torch.optim.AdamW(list(trainable(model).values()), lr=1e-3,
                             betas=(0.9, 0.999), eps=1e-8, weight_decay=0.0)

def copied_values(model, gradient=False):
    return {n: (p.grad if gradient else p).detach().clone()
            for n, p in trainable(model).items()}

def manual(mode):
    model = copy.deepcopy(initial).train()
    optim = optimizer(model)
    sums, counts = [], []
    for row in examples:
        inputs = collate([row])
        labels = inputs.pop('labels')
        # Independent loss: no labels or loss kwargs passed to the model.
        logits = model(**inputs, use_cache=False, logits_to_keep=0).logits
        target = labels[:, 1:].reshape(-1)
        total = F.cross_entropy(logits[:, :-1, :].float().reshape(-1, 32), target,
                                ignore_index=-100, reduction='sum')
        sums.append(total)
        counts.append(int(target.ne(-100).sum()))
    loss = (sum(s / n for s, n in zip(sums, counts)) / len(counts)
            if mode == 'parent' else sum(sums) / sum(counts))
    loss.backward()
    grads = copied_values(model, True)
    optim.step()
    return {'loss': loss.item(), 'counts': counts,
            'per_example_mean': [s.item() / n for s, n in zip(sums, counts)],
            'gradients': grads, 'parameters': copied_values(model)}

class Capture(TrainerCallback):
    def __init__(self):
        self.gradients = None
        self.updates = 0

    def on_pre_optimizer_step(self, args, state, control, model=None, **kwargs):
        self.gradients = copied_values(model, True)

    def on_optimizer_step(self, args, state, control, **kwargs):
        self.updates += 1

def native(accepts):
    model = copy.deepcopy(initial)
    forwards = []
    def observe(module, args, kwargs):
        forwards.append({'kwargs': sorted(kwargs),
                         'num_items_in_batch': (int(kwargs['num_items_in_batch'])
                                                if 'num_items_in_batch' in kwargs else None),
                         'supervised_tokens': int(kwargs['labels'][:, 1:].ne(-100).sum())})
    hook = model.register_forward_pre_hook(observe, with_kwargs=True)
    capture = Capture()
    optim = optimizer(model)
    out = HERE / ('native-parent' if not accepts else 'native-pooled')
    out.mkdir(exist_ok=True)
    args = TrainingArguments(output_dir=str(out), use_cpu=True, max_steps=1,
        per_device_train_batch_size=1, gradient_accumulation_steps=2,
        learning_rate=1e-3, lr_scheduler_type='constant', warmup_steps=0,
        max_grad_norm=0.0, weight_decay=0.0, seed=3407, data_seed=3407,
        report_to='none', disable_tqdm=True, save_strategy='no', logging_strategy='no',
        dataloader_pin_memory=False, dataloader_num_workers=0, remove_unused_columns=False,
        bf16=False, fp16=False, label_smoothing_factor=0.0)
    trainer = Trainer(model=model, args=args, train_dataset=examples,
                      data_collator=collate, callbacks=[capture], optimizers=(optim, None))
    detected = trainer.model_accepts_loss_kwargs
    trainer.model_accepts_loss_kwargs = accepts
    result = trainer.train()
    hook.remove()
    assert trainer.compute_loss_func is None and trainer.label_smoother is None
    assert trainer.state.global_step == capture.updates == 1 and len(forwards) == 2
    assert trainer.current_gradient_accumulation_steps == 2
    return {'loss': result.training_loss, 'gradients': capture.gradients,
            'parameters': copied_values(model), 'forwards': forwards,
            'detected_model_accepts_loss_kwargs': detected,
            'model_accepts_loss_kwargs': trainer.model_accepts_loss_kwargs,
            'trainer_accumulation_steps': trainer.current_gradient_accumulation_steps,
            'accelerator_accumulation_steps': trainer.accelerator.gradient_accumulation_steps,
            'optimizer_updates': capture.updates}

def distance(a, b):
    x = torch.cat([a[n].reshape(-1).double() for n in sorted(a)])
    y = torch.cat([b[n].reshape(-1).double() for n in sorted(b)])
    return {'max_abs': float((x - y).abs().max()),
            'relative_l2': float(torch.linalg.vector_norm(x - y) / torch.linalg.vector_norm(y)),
            'reference_l2': float(torch.linalg.vector_norm(y))}

parent, pooled = manual('parent'), manual('pooled')
flag_false, flag_true = native(False), native(True)
comparisons = {}
for label, actual, expected in [('flag_false_vs_parent', flag_false, parent),
                                ('flag_true_vs_pooled', flag_true, pooled),
                                ('flag_false_vs_pooled', flag_false, pooled)]:
    comparisons[label] = {'loss_abs': abs(actual['loss'] - expected['loss']),
                          'gradient': distance(actual['gradients'], expected['gradients']),
                          'updated_parameters': distance(actual['parameters'], expected['parameters'])}
for key in ['flag_false_vs_parent', 'flag_true_vs_pooled']:
    assert comparisons[key]['loss_abs'] < 1e-6
    assert comparisons[key]['gradient']['max_abs'] < 2e-6
    assert comparisons[key]['gradient']['relative_l2'] < 2e-5
    assert comparisons[key]['updated_parameters']['max_abs'] < 2e-6
assert comparisons['flag_false_vs_pooled']['gradient']['relative_l2'] > 0.05
assert comparisons['flag_false_vs_pooled']['updated_parameters']['max_abs'] > 1e-5
assert all(f['num_items_in_batch'] is None for f in flag_false['forwards'])
assert all(f['num_items_in_batch'] == 7 for f in flag_true['forwards'])
assert flag_false['accelerator_accumulation_steps'] == 1
source = Path(inspect.getsourcefile(Trainer))
report = {'status': 'PASS', 'versions': {'python': platform.python_version(),
    'torch': torch.__version__, 'transformers': transformers.__version__,
    'peft': peft.__version__, 'accelerate': accelerate.__version__},
    'trainer_source': str(source), 'trainer_source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'supervised_tokens': parent['counts'], 'per_example_mean_losses': parent['per_example_mean'],
    'manual_parent_loss': parent['loss'], 'manual_pooled_loss': pooled['loss'],
    'native_flag_false': {k: v for k, v in flag_false.items() if k not in ('gradients', 'parameters')},
    'native_flag_true': {k: v for k, v in flag_true.items() if k not in ('gradients', 'parameters')},
    'comparisons': comparisons,
    'limitations': ['CPU float32 random tiny Gemma4 with nonzero LoRA; no pretrained weights, GPU, NF4 or distributed test.',
                    'One AdamW update, microbatch 1, two accumulated examples; no clipping, smoothing, custom loss or dropout.',
                    'Does not establish convergence or translation merit; production flags still require binding.']}
(HERE / 'result.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report, indent=2))
