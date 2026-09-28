"""Offline random-weight CPU canary; never downloads a checkpoint."""
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import sys


def main():
    for key in ('HF_HUB_OFFLINE', 'TRANSFORMERS_OFFLINE', 'HF_HUB_DISABLE_TELEMETRY'):
        os.environ[key] = '1'
    hub_site = Path(__file__).resolve().parents[1] / 'resources/local/hf-client-venv/Lib/site-packages'
    if hub_site.is_dir():
        sys.path.append(str(hub_site))  # Existing science packages keep precedence.
    packages = {}
    for name in ('torch', 'transformers', 'huggingface_hub', 'tokenizers', 'jinja2'):
        module = importlib.import_module(name)
        packages[name] = {'version': importlib.metadata.version(name), 'path': module.__file__}
    import torch
    from transformers import (Qwen3_5TextConfig, Qwen3_5ForCausalLM, LogitsProcessorList,
                              TemperatureLogitsWarper, TopKLogitsWarper, TopPLogitsWarper, MinPLogitsWarper)
    from cloud_pilot.qwen_presence import GeneratedTokenPresencePenalty

    torch.set_num_threads(1)
    torch.manual_seed(42)
    config = Qwen3_5TextConfig(vocab_size=32, hidden_size=32, intermediate_size=48,
        num_hidden_layers=2, layer_types=['linear_attention', 'full_attention'],
        num_attention_heads=4, num_key_value_heads=2, head_dim=8,
        linear_num_key_heads=2, linear_num_value_heads=2,
        linear_key_head_dim=8, linear_value_head_dim=8, linear_conv_kernel_dim=4,
        max_position_embeddings=64, pad_token_id=0,
        rope_parameters={'rope_type': 'default', 'rope_theta': 10000.,
                         'partial_rotary_factor': .5, 'mrope_section': [1, 1, 0]})
    config._attn_implementation = 'eager'
    model = Qwen3_5ForCausalLM(config).cpu().eval()
    ids = torch.tensor([[1, 2, 3, 4]])
    processor = GeneratedTokenPresencePenalty(ids.shape[1])
    expected_processors = LogitsProcessorList([processor, TemperatureLogitsWarper(.7),
        TopKLogitsWarper(20), TopPLogitsWarper(.8), MinPLogitsWarper(0.)])
    options = dict(input_ids=ids, attention_mask=torch.ones_like(ids), max_new_tokens=3,
        do_sample=True, temperature=.7, top_p=.8, top_k=20, min_p=0., repetition_penalty=1.,
        logits_processor=[processor], use_cache=True, logits_to_keep=1,
        return_dict_in_generate=True, output_scores=True, output_logits=True)
    with torch.inference_mode():
        torch.manual_seed(42)
        output = model.generate(**options)
        torch.manual_seed(42)
        repeated = model.generate(**options)
    assert output.sequences.shape == (1, 7)
    torch.testing.assert_close(output.sequences, repeated.sequences)
    for index, (raw, processed) in enumerate(zip(output.logits, output.scores)):
        assert raw.shape == (1, 32)
        expected = expected_processors(output.sequences[:, :ids.shape[1] + index], raw.clone())
        torch.testing.assert_close(processed, expected)
    assert len(output.scores) == 3
    assert output.past_key_values is not None
    assert output.past_key_values.get_seq_length() == 6
    print(json.dumps({'status': 'PASS', 'packages': packages, 'device': str(model.device),
        'parameters': sum(p.numel() for p in model.parameters()), 'layer_types': config.layer_types,
        'generated_ids': output.sequences.tolist(), 'cache': type(output.past_key_values).__name__,
        'cache_sequence_length': output.past_key_values.get_seq_length(),
        'same_seed_repeat': True, 'custom_processor_before_warpers': True,
        'logits_to_keep': 1, 'checkpoint_loaded': False}, indent=2))


if __name__ == '__main__':
    main()
