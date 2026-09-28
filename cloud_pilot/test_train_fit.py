"""Frozen-input, first-attempt and real random-Gemma CPU checks (no pretrained weights)."""
import copy
from collections import Counter
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from uuid import uuid4

from . import train_fit as fit

ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "experiments/train-audit-20260927/qualified-v1/train.jsonl"
INPUTS = ROOT / "experiments/train-recall-20260927/inputs.jsonl"
CONTROL = ROOT / "experiments/train-fit-20260927/source-control.json"
TOKENIZER = ROOT / "resources/local/cloud-pilot-qualified-20260927/tokenizer"
DEADLINE = "2099-01-01T00:00:00+00:00"
HAS_CPU_STACK = all(importlib.util.find_spec(name) is not None for name in ("torch", "transformers", "peft"))


class FitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = fit.read_inputs(INPUTS, fit.INPUTS_SHA256, TRAIN)
        cls.control = fit.read_source_control(CONTROL, fit.SOURCE_CONTROL_SHA256, cls.rows)

    def test_bound_inputs_control_schedule_and_audit(self):
        self.assertEqual(len(self.rows), 20)
        for path, digest, call in ((INPUTS, fit.INPUTS_SHA256, lambda p, h: fit.read_inputs(p, h, TRAIN)),
                                  (CONTROL, fit.SOURCE_CONTROL_SHA256, lambda p, h: fit.read_source_control(p, h, self.rows))):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "checksum"):
                call(path, "0" * 64)
        bad = copy.deepcopy(self.control)
        bad["pairs"][0]["mismatched_source_parent_id"] = self.rows[0]["id"]
        with self.assertRaisesRegex(ValueError, "permutation"):
            fit.validate_control(bad, self.rows)
        ordered = fit.schedule(self.rows)
        ids = [fit.output_id(*item) for item in ordered]
        self.assertEqual(len(ids), 80)
        self.assertEqual(len(set(ids)), 80)
        self.assertEqual(Counter((enabled, condition) for _, enabled, condition in ordered),
                         {condition: 20 for condition in fit.CONDITIONS})
        for i, row in enumerate(self.rows):
            self.assertEqual(ordered[i * 4:(i + 1) * 4],
                [(row, *condition) for condition in fit.CONDITIONS[i % 4:] + fit.CONDITIONS[:i % 4]])
        audit_path = ROOT / "experiments/train-fit-20260927/token-audit.json"
        self.assertEqual(fit.runtime.digest(audit_path), fit.TOKEN_AUDIT_SHA256)
        audit = fit.runtime.read_json(audit_path)
        prepared = {r["id"] + ":" + r["source_condition"]: r for r in audit["rows"]}
        self.assertEqual(fit.validate_token_map(prepared), fit.TOKEN_MAP_SHA256)
        for field in ("input_tokens", "supervised_tokens", "input_ids_sha256", "labels_sha256", "target_ids_sha256"):
            corrupt = copy.deepcopy(prepared)
            item = next(iter(corrupt.values()))
            item[field] = item[field] + 1 if isinstance(item[field], int) else "0" * 64
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "token map"):
                fit.validate_token_map(corrupt)
        for name, expected in fit.HELPER_SHA256.items():
            self.assertEqual(fit.runtime.digest(ROOT / "cloud_pilot" / name), expected)

    def test_first_attempt_durability_and_stop(self):
        audit = fit.runtime.read_json(ROOT / "experiments/train-fit-20260927/token-audit.json")
        prepared = {r["id"] + ":" + r["source_condition"]: r for r in audit["rows"]}
        ordered = [fit.output_id(*item) for item in fit.schedule(self.rows)]
        for fail_at in (None, 1, 80):
            output = ROOT / "resources/local/train-fit-test-tmp" / uuid4().hex
            output.mkdir(parents=True)
            run = {"status": "running", "schedule": ordered, "identity_sha256": "test-identity", "scheduled_outputs": 80,
                "attempted_outputs": 0, "recorded_outputs": 0, "completed_outputs": 0, "completed_cases": 0,
                "active_output_id": None, "unattempted_output_ids": ordered.copy()}
            calls = []

            def forward(model, item, enabled, deadline):
                calls.append((item, enabled))
                durable = fit.runtime.read_json(output / "run.json")
                self.assertEqual(durable["attempted_outputs"], len(calls))
                self.assertEqual(durable["active_output_id"], ordered[len(calls) - 1])
                if len(calls) == fail_at:
                    raise TimeoutError("first attempt timeout")
                return {"sum_nll": 2.0 * item["supervised_tokens"], "mean_nll": 2.0,
                        "supervised_tokens": item["supervised_tokens"], "model_loss": 2.0}

            with patch.object(fit, "forward_once", side_effect=forward), patch("sys.stdout", new=io.StringIO()):
                if fail_at:
                    with self.assertRaisesRegex(TimeoutError, "first attempt"):
                        fit.run_forwards(object(), self.rows, prepared, output, run, DEADLINE)
                else:
                    fit.run_forwards(object(), self.rows, prepared, output, run, DEADLINE)
            durable = fit.runtime.read_json(output / "run.json")
            results = [json.loads(line) for line in (output / "results.jsonl").read_text("utf-8").splitlines()]
            self.assertEqual(durable["status"], "incomplete" if fail_at else "completed")
            self.assertEqual(len(calls), fail_at or 80)
            self.assertEqual(durable["recorded_outputs"], len(results))
            self.assertEqual([r["id"] for r in results], ordered[:fail_at or 80])
            self.assertEqual(durable["unattempted_output_ids"], ordered[fail_at or 80:])
            self.assertIsNone(durable["active_output_id"])
            successful = fail_at - 1 if fail_at else 80
            self.assertEqual(durable["completed_outputs"], successful)
            self.assertEqual(durable["completed_cases"], successful // 4)
            if fail_at:
                self.assertEqual(results[-1]["status"], "error")
                self.assertIsNone(results[-1]["sum_nll"])
            for result in results:
                item = prepared[result["case_id"] + ":" + result["source_condition"]]
                self.assertEqual(result["input_sha256"], item["input_ids_sha256"])
                self.assertEqual(result["labels_sha256"], item["labels_sha256"])

    def test_deadline_before_first_forward(self):
        output = ROOT / "resources/local/train-fit-test-tmp" / uuid4().hex
        output.mkdir(parents=True)
        ordered = [fit.output_id(*item) for item in fit.schedule(self.rows)]
        run = {"status": "running", "schedule": ordered, "attempted_outputs": 0, "recorded_outputs": 0,
            "completed_outputs": 0, "completed_cases": 0, "active_output_id": None, "unattempted_output_ids": ordered}
        with patch.object(fit, "forward_once") as forward, self.assertRaises(TimeoutError):
            fit.run_forwards(object(), self.rows, {}, output, run, "2000-01-01T00:00:00+00:00")
        forward.assert_not_called()
        self.assertEqual(run["attempted_outputs"], 0)
        self.assertEqual(run["unattempted_output_ids"], ordered)

    @unittest.skipUnless(HAS_CPU_STACK, "Run with science Python plus process-local pinned PEFT/HF paths for native CPU check")
    def test_real_tokenizer_exact_saved_arrays_and_unchanged_target(self):
        from transformers import AutoTokenizer
        fit.runtime.checked_files(TOKENIZER, fit.bundle.TOKENIZER_HASHES)
        tokenizer = AutoTokenizer.from_pretrained(TOKENIZER, local_files_only=True, trust_remote_code=False)
        prepared = fit.prepare_inputs(self.rows, TRAIN, self.control, tokenizer, 2048)
        self.assertEqual(fit.validate_token_map(prepared), fit.TOKEN_MAP_SHA256)
        self.assertEqual(len(prepared), 40)
        for row in self.rows:
            first, second = [prepared[row["id"] + ":" + condition] for condition in ("correct", "mismatched")]
            self.assertEqual(first["input_ids"][first["prompt_tokens"]:], second["input_ids"][second["prompt_tokens"]:])
        with self.assertRaisesRegex(ValueError, "context overflow"):
            fit.prepare_inputs(self.rows, TRAIN, self.control, tokenizer, 2)
        corrupt = copy.deepcopy(self.rows)
        corrupt[0]["source_text"] += " changed"
        with self.assertRaises(ValueError):
            fit.prepare_inputs(corrupt, TRAIN, self.control, tokenizer, 2048)

    @unittest.skipUnless(HAS_CPU_STACK, "Run with science Python plus process-local pinned PEFT/HF paths for native CPU check")
    def test_native_gemma_causal_loss_and_nonzero_peft_restoration(self):
        import torch
        from transformers import Gemma4Config, Gemma4TextConfig, Gemma4ForConditionalGeneration
        from peft import LoraConfig, get_peft_model
        torch.set_num_threads(1)
        torch.manual_seed(42)
        config = Gemma4Config(text_config=Gemma4TextConfig(vocab_size=32, hidden_size=32, intermediate_size=48,
            num_hidden_layers=2, num_attention_heads=4, num_key_value_heads=2, head_dim=8, global_head_dim=8,
            max_position_embeddings=64, vocab_size_per_layer_input=32, hidden_size_per_layer_input=0,
            layer_types=["sliding_attention", "full_attention"], sliding_window=16, final_logit_softcapping=30.0))
        config._attn_implementation = "eager"
        base = Gemma4ForConditionalGeneration(config)
        model = get_peft_model(base, LoraConfig(r=2, lora_alpha=4, target_modules=["q_proj", "v_proj"],
            lora_dropout=0.0, task_type="CAUSAL_LM", bias="none"))
        with torch.no_grad():
            for name, parameter in model.named_parameters():
                if "lora_B" in name:
                    parameter.normal_(0.0, 0.2)  # nonzero adapter: toggles must change the actual logits
        model.eval()
        model.requires_grad_(False)
        ids = [2, 3, 4, 7, 8, 1]
        labels = [-100, -100, -100, 7, 8, 1]
        prepared = {"input_ids": ids, "labels": labels, "attention_mask": [1] * 6, "supervised_tokens": 3}
        for dtype in (torch.float32, torch.bfloat16):
            model.to(dtype=dtype)
            tensor_ids, tensor_labels = torch.tensor([ids]), torch.tensor([labels])
            with torch.inference_mode():
                output = model(input_ids=tensor_ids, attention_mask=torch.ones_like(tensor_ids), labels=tensor_labels,
                               use_cache=False, logits_to_keep=0, return_dict=True)
            self.assertEqual(tuple(output.logits.shape), (1, 6, 32))
            self.assertIsNone(output.past_key_values)
            nll = fit.causal_nll(output.logits, tensor_labels, output.loss)
            expected = -torch.log_softmax(output.logits[0, 2:5].float(), dim=-1)[torch.arange(3), torch.tensor([7, 8, 1])].sum().item()
            self.assertAlmostEqual(nll["sum_nll"], expected, places=5)
            self.assertEqual(nll["supervised_tokens"], 3)
            changed_prompt = output.logits.clone()
            changed_prompt[:, :2, :] += 5000.0 * torch.arange(32)
            self.assertEqual(fit.causal_nll(changed_prompt, tensor_labels, output.loss), nll)
            with self.assertRaisesRegex(ValueError, "disagrees"):
                fit.causal_nll(output.logits, tensor_labels, output.loss + 1.0)
            corrupt = output.logits.clone()
            corrupt[0, 0, 0] = float("nan")
            with self.assertRaisesRegex(ValueError, "Nonfinite"):
                fit.causal_nll(corrupt, tensor_labels, output.loss)
            measured = [fit.forward_once(model, prepared, enabled, DEADLINE) for enabled in (False, True, False, True)]
            self.assertEqual(measured[0]["sum_nll"], measured[2]["sum_nll"])
            self.assertEqual(measured[1]["sum_nll"], measured[3]["sum_nll"])
            self.assertGreater(abs(measured[0]["sum_nll"] - measured[1]["sum_nll"]), 1e-5)
            for enabled, result in zip((False, True, False, True), measured):
                self.assertEqual(result["adapter_state"]["during"]["enabled"], enabled)
                self.assertTrue(result["adapter_state"]["restored"]["enabled"])
            with patch.object(model, "forward", side_effect=RuntimeError("failed forward")), self.assertRaisesRegex(RuntimeError, "failed forward"):
                fit.forward_once(model, prepared, False, DEADLINE)
            self.assertTrue(fit.adapter_state(model, True)["enabled"])
            # A completed GPU kernel may cross the deadline: it remains a failed first attempt.
            with patch.object(fit.runtime, "check_deadline", side_effect=[None, TimeoutError("after forward")]), self.assertRaisesRegex(TimeoutError, "after forward"):
                fit.forward_once(model, prepared, False, DEADLINE)
            self.assertTrue(fit.adapter_state(model, True)["enabled"])


if __name__ == "__main__":
    unittest.main()
