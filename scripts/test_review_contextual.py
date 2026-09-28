"""Offline fixtures use real frozen inputs/tokenizer; no actual experiment outputs or semantic reviews."""
from collections import Counter
import copy
import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
SCRATCH = ROOT / "resources/local/contextual-review-check"
SCRATCH.mkdir(parents=True, exist_ok=True)
os.environ.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", HF_HUB_DISABLE_TELEMETRY="1", HF_HOME=str(SCRATCH / "hf-cache"))
sys.path[:0] = [str(ROOT), str(ROOT / "resources/local/train-fit-deps"), str(ROOT / "resources/local/hf-client-venv/Lib/site-packages")]
from transformers import AutoTokenizer
from scripts import review_contextual as mod

PACKAGE = ROOT / "resources/local/contextual-run-package"
TOKENIZER = ROOT / "resources/local/cloud-pilot-qualified-20260927/tokenizer"
ATTEMPT = ROOT / "experiments/contextual-supervision-20260927/attempt-2"


class ContextualReviewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract, cls.rows, cls.references, cls.assessments, _ = mod.prep.load_contract()
        cls.execution = json.loads((ATTEMPT / "execution.json").read_bytes())
        cls.preparation = json.loads((ATTEMPT / "execution-preparation.json").read_bytes())
        _, cls.payload = mod.driver.read_package(PACKAGE, mod.driver.PACKAGE_SHA256)
        mod.driver.runtime.checked_files(TOKENIZER, mod.driver.bundle.TOKENIZER_HASHES)
        cls.tokenizer = AutoTokenizer.from_pretrained(TOKENIZER, local_files_only=True, trust_remote_code=False)
        cls.prompts = mod.driver.prepare_prompts(cls.rows, cls.payload["dev-prompt-identities.json"], cls.tokenizer, 262144)

    def fixture(self, count=48, failed=False):
        d, q = mod.driver, mod.prep.shared
        slots = [s["control_id"] for s in self.payload["ordered-slots.jsonl"]]
        training = dict(status="completed", settings=d.SETTINGS, runner_sha256=d.HELPER_SHA256["contextual_train.py"],
            runtime_sha256=d.HELPER_SHA256["runtime.py"], scheduled_parent_ids=slots, scheduled_slots_per_arm=768,
            initial_adapter_sha256="1" * 64, arms={})
        adapters = {}
        for n, arm in enumerate(mod.ARMS, 2):
            files = {"adapter_config.json": mod.sha(b'{}'), "adapter_model.safetensors": str(n) * 64}
            training["arms"][arm] = dict(status="completed", completed_steps=48, consumed_slots=768,
                consumed_parent_ids=slots, parent_order_verified=True, optimizer_initially_empty=True,
                optimizer_initial_state_entries=0, initial_scheduler_step=0, model_accepts_loss_kwargs=False,
                initial_adapter_sha256="1" * 64, initial_rng_sha256="4" * 64, train_begin_rng_sha256="5" * 64,
                adapter_files=files, final_adapter_sha256=str(n) * 64)
            adapters[arm] = dict(files=files, final_tensor_sha256=str(n) * 64, new_phase_steps=48, original_adapter_step=280)
        identity = dict(experiment_id="contextual-supervision-20260927", package_manifest_sha256=d.PACKAGE_SHA256,
            qualified_train_sha256=q.TRAIN_SHA256, evaluation_inputs_sha256=d.frozen.INPUTS_SHA256, inputs_sha256=d.frozen.INPUTS_SHA256,
            original_adapter_files=q.ADAPTER_FILES, original_adapter_manifest_sha256=q.ADAPTER_MANIFEST_SHA256,
            model_id=d.runtime.MODEL_ID, model_revision=d.runtime.REVISION, tokenizer_files=d.bundle.TOKENIZER_HASHES,
            runner_sha256=self.preparation["script_hashes"]["contextual_run.py"], helper_sha256=d.HELPER_SHA256,
            settings=d.SETTINGS, seed=42, decoding="greedy", enable_thinking=False, max_new_tokens=4096,
            max_generation_seconds=1200, eos_token_ids=d.protocol.EOS, evaluation_prompt="dev_assisted.messages(row, plain, [])",
            uniform_evaluation_contract_sha256=mod.prep.CONTRACT_SHA, prompts=self.payload["dev-prompt-identities.json"],
            expert_adjudicated=False, quality_validated=False, scoring_performed=False, base_files={}, environment={},
            deadline_utc="2026-09-27T15:30:00+00:00", adapters=adapters)
        ids = [r["id"] + ":" + arm for r, arm in mod.ordered(self.rows)]
        predictions = []
        for i, (row, arm) in enumerate(mod.ordered(self.rows)[:count], 1):
            tokens = self.tokenizer.encode("offline fixture", add_special_tokens=False) + [1]
            status = "success"
            if failed and i == count:
                tokens, status = [], "error"
            text = self.tokenizer.decode(tokens, skip_special_tokens=True)
            predictions.append(dict(id=ids[i-1], case_id=row["id"], record_id=row["record_id"], work_id=row["work_id"],
                arm=arm, condition=arm, sequence=i, input_sha256=mod.sha(row["source_text"].encode()),
                identity_sha256=mod.sha(mod.canonical(identity)), adapter_sha256=adapters[arm]["files"]["adapter_model.safetensors"],
                input_tokens=len(self.prompts[row["id"]]), rendered_input_ids_sha256=mod.sha(mod.canonical(self.prompts[row["id"]])),
                text=text, output_token_ids=tokens, output_tokens=len(tokens), output_sha256=mod.sha(text.encode()),
                elapsed_seconds=1.0, status=status, hit_output_cap_without_eos=False, stop_reason=None))
        completed = predictions[:-1] if failed else predictions
        cases = sum(sum(p["case_id"] == row["id"] for p in completed) == 2 for row in self.rows)
        status = "completed" if count == 48 and not failed else "incomplete"
        evaluation = dict(identity, identity_sha256=mod.sha(mod.canonical(identity)), status=status, schedule=ids,
            scheduled_outputs=48, attempted_outputs=count, recorded_outputs=count, completed_outputs=len(completed),
            completed_cases=cases, active_output_id=None, unattempted_output_ids=ids[count:], canary={"status": "passed"})
        top = dict(identity, status=status, training_canary={"status": "passed"}, training_steps_per_arm=48,
            evaluation_completed_outputs=len(completed), evaluation_completed_cases=cases)
        return top, training, evaluation, predictions

    def validate(self, values):
        return mod.validate_artifacts(*values, self.rows, self.preparation, self.payload, self.tokenizer)

    def files(self, values):
        return mod.build_files(values[3], {}, self.validate(values), self.contract, self.rows, self.references, self.assessments)

    def ratings(self, files):
        packets, reviews = {}, {}
        for reviewer in mod.SEEDS:
            packets[reviewer] = mod.prep.decode_lines(files[f"reviewer-{reviewer}/packet.jsonl"])
            reviews[reviewer] = []
            for p in packets[reviewer]:
                status = p["execution_status"]
                whole = p["assessment"] == "provisional_whole_translation"
                reviews[reviewer].append(dict(review_id=p["review_id"], output_sha256=p["output_sha256"],
                    judgment=("accepted" if whole else "constrained_only") if status == "success" else "not_assessable",
                    categories={c: "pass" if status == "success" else "uncertain" for c in mod.prep.CATEGORIES},
                    supported_span_severity="none" if status == "success" else "uncertain",
                    unknown_span_handling="no_unknown_span" if status == "success" else "uncertain",
                    reason="Synthetic test rating; not a semantic assessment.", output_span=""))
        return packets, reviews

    def test_launch_and_actual_tokenizer_complete_fixture(self):
        mod.validate_launch(self.execution, self.preparation)
        self.assertTrue(self.validate(self.fixture())["complete"])
        altered = copy.deepcopy(self.execution)
        altered["run_id"] = "f" * 32
        with self.assertRaisesRegex(ValueError, "launch"):
            mod.validate_launch(altered, self.preparation)

    def test_default96_unchanged_explicit48_and_rubric(self):
        files = self.files(self.fixture())
        packets, reviews = self.ratings(files)
        p, r = packets["A"], reviews["A"]
        with self.assertRaisesRegex(ValueError, "coverage"):
            mod.scoring.validate_reviews(p, r)
        self.assertEqual(len(mod.scoring.validate_reviews(p, r, expected_count=48)), 48)
        p96, r96 = copy.deepcopy(p) + copy.deepcopy(p), copy.deepcopy(r) + copy.deepcopy(r)
        for i in range(48, 96):
            p96[i]["review_id"] += "extra"
            r96[i]["review_id"] += "extra"
        self.assertEqual(len(mod.scoring.validate_reviews(p96, r96)), 96)
        next(item for item in r if item['judgment'] == 'accepted')["categories"]["lexical_meaning"] = "fail"
        with self.assertRaises(ValueError):
            mod.scoring.validate_reviews(p, r, expected_count=48)

    def test_blind_packets_reference_bytes_and_reused_instructions(self):
        files = self.files(self.fixture())
        seen = []
        for reviewer in mod.SEEDS:
            packet = mod.prep.decode_lines(files[f"reviewer-{reviewer}/packet.jsonl"])
            self.assertEqual(len(packet), 48)
            self.assertTrue(all(set(p) == mod.prep.PACKET_FIELDS for p in packet))
            self.assertEqual(files[f"reviewer-{reviewer}/INSTRUCTIONS.md"].replace(b"Review all 48", b"Review all 96"), mod.prep.instructions())
            seen.append({p["review_id"] for p in packet})
            for p in packet:
                ref = next(r for r in self.references.values() if r["source_text"] == p["source_text"])
                self.assertEqual(p["references"], {k: ref[k] for k in p["references"]})
        self.assertFalse(seen[0] & seen[1])
        self.assertEqual(files["lead-only/frozen/references.jsonl"], (mod.prep.DEV / "references.jsonl").read_bytes())

    def test_missing_failed_and_no_evaluation_keep48_inconclusive(self):
        values = self.fixture(3, failed=True)
        files = self.files(values)
        packets, reviews = self.ratings(files)
        self.assertEqual(Counter(p["execution_status"] for p in packets["A"]), {"success": 2, "error": 1, "unattempted": 45})
        mapping = mod.prep.decode_lines(files["lead-only/mapping.jsonl"])
        report = mod.summarize(mapping, packets, reviews, self.contract, self.validate(values))
        self.assertEqual(report["screen_status"], "inconclusive")
        self.assertIsNone(report["both_reviewers_screen"])
        top, training, _, _ = self.fixture(0)
        self.assertFalse(self.validate((top, training, None, []))["complete"])

    def test_token_source_order_counters_and_adapter_tampering(self):
        for mutate in (
            lambda v: v[3][0].update(output_sha256="f"*64),
            lambda v: v[3][0]["output_token_ids"].__setitem__(0, 2),
            lambda v: v[3][0].update(input_sha256="f"*64),
            lambda v: v[3][0].update(rendered_input_ids_sha256="f"*64),
            lambda v: v[3].reverse(),
            lambda v: v[3][0].update(attempt=2),
            lambda v: v[2].update(attempted_outputs=49),
            lambda v: v[2].update(active_output_id="pending"),
            lambda v: v[3][0].update(adapter_sha256="f"*64),
            lambda v: v[1]["arms"]["candidate"].update(initial_rng_sha256="f"*64),
        ):
            with self.subTest(mutate=mutate):
                values = self.fixture()
                mutate(values)
                with self.assertRaises(ValueError):
                    self.validate(values)

    def test_uniform_screen_exact_parity_and_disagreements(self):
        values = self.fixture()
        files = self.files(values)
        packets, reviews = self.ratings(files)
        mapping = mod.prep.decode_lines(files["lead-only/mapping.jsonl"])
        # Two control meaning errors on different works become candidate acceptance.
        gains = []
        for m in mapping:
            if m["reviewer"] == "A" and m["condition"] == "control" and m["assessment"] == "provisional_whole_translation" and m["work_id"] not in [x[1] for x in gains]:
                gains.append((m["case_id"], m["work_id"]))
                if len(gains) == 2: break
        for m in mapping:
            if m["condition"] == "control" and m["case_id"] in {g[0] for g in gains}:
                rating = next(r for r in reviews[m["reviewer"]] if r["review_id"] == m["review_id"])
                p = next(p for p in packets[m["reviewer"]] if p["review_id"] == m["review_id"])
                rating.update(judgment="meaning_error", supported_span_severity="meaning_error", output_span=p["output_text"])
                rating["categories"]["lexical_meaning"] = "fail"
        report = mod.summarize(mapping, packets, reviews, self.contract, self.validate(values))
        self.assertTrue(report["both_reviewers_screen"])
        for reviewer in mod.SEEDS:
            decoded = {a: {} for a in mod.ARMS}
            ratings = mod.prep.unique(reviews[reviewer], "review_id")
            for m in mapping:
                if m["reviewer"] == reviewer: decoded[m["condition"]][m["case_id"]] = {**ratings[m["review_id"]], **m}
            expected = mod.scoring.paired_report(decoded["control"], decoded["candidate"], self.contract["comparison"]["screen"], True)
            expected["screen_checks"]["full_two_arm_comparison_complete"] = expected["screen_checks"].pop("full_four_condition_comparison_complete")
            self.assertEqual(report["reviewers"][reviewer]["paired"]["control -> candidate"], expected)
            self.assertEqual(report["reviewers"][reviewer]["conditions"]["candidate"]["whole_denominator"], 15)
            by_work = report["reviewers"][reviewer]["conditions"]["candidate"]["by_work"]
            self.assertEqual(sum(r["whole_denominator"] for r in by_work.values()), 15)
            self.assertEqual(sum(r["constrained_denominator"] for r in by_work.values()), 9)
            self.assertTrue(all(r["whole_denominator"] > 0 for r in by_work.values()))

    def recovery_fixture(self):
        top, training, evaluation, predictions = values = self.fixture()
        folder = SCRATCH / uuid.uuid4().hex
        run = folder / "recovered/contextual"
        raw = {"run.json": mod.prep.json_bytes(top), "training/run.json": mod.prep.json_bytes(training),
               "evaluation/run.json": mod.prep.json_bytes(evaluation), "evaluation/predictions.jsonl": mod.prep.lines(predictions)}
        for arm in mod.ARMS:
            raw[f"training/{arm}/adapter/adapter_config.json"] = b'{}'
        for name, data in raw.items():
            path = run / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        export = dict(self.preparation, operation="contextual_pilot", quality_validated=False, contextual_status="complete",
            files={"contextual/"+n: {"bytes": len(data), "sha256": mod.sha(data)} for n, data in raw.items()})
        for arm in mod.ARMS:
            export['files'][f'contextual/training/{arm}/adapter/adapter_model.safetensors'] = {
                'bytes': 128, 'sha256': training['arms'][arm]['adapter_files']['adapter_model.safetensors']}
        manifest_bytes = mod.prep.json_bytes(export)
        (run.parent / "manifest.json").write_bytes(manifest_bytes)
        prefix = self.preparation['output_prefix']
        inventory = {prefix + '/' + n: dict(bytes=r['bytes'], xet_hash='synthetic-committed-object') for n, r in export['files'].items()}
        inventory[prefix + '/manifest.json'] = dict(bytes=len(manifest_bytes), xet_hash='synthetic-committed-manifest')
        proof = dict(run_id=self.preparation['run_id'], manifest_sha256=mod.sha(manifest_bytes),
            provider_inventory_committed=True, provider_inventory=inventory,
            local_sha_verified_files=['contextual/'+n for n in raw], model_weights_downloaded=False, contextual_status='complete')
        (folder / 'recovery.json').write_bytes(mod.prep.json_bytes(proof))
        return folder, run, raw, export, proof, training

    def test_recovery_manifest_inventory_and_adapter_export_binding(self):
        folder, run, raw, export, proof, training = self.recovery_fixture()
        manifest = (run.parent/'manifest.json').read_bytes()
        mod.validate_recovery(run.parent, manifest, export, proof, self.preparation)
        mod.validate_adapter_exports(training, export)
        changed = copy.deepcopy(export)
        changed['untrusted_replacement'] = True
        with self.assertRaisesRegex(ValueError, 'binding'):
            mod.validate_recovery(run.parent, mod.prep.json_bytes(changed), changed, proof, self.preparation)
        for mutate in (
            lambda p: p.update(provider_inventory_committed=False),
            lambda p: p.update(run_id='f'*32),
            lambda p: p['provider_inventory'].pop(next(iter(p['provider_inventory']))),
            lambda p: p['local_sha_verified_files'].pop(),
            lambda p: p['provider_inventory'][self.preparation['output_prefix']+'/manifest.json'].update(xet_hash=''),
        ):
            altered = copy.deepcopy(proof)
            mutate(altered)
            with self.assertRaises(ValueError):
                mod.validate_recovery(run.parent, manifest, export, altered, self.preparation)
        for arm in mod.ARMS:
            name = f'contextual/training/{arm}/adapter/adapter_model.safetensors'
            wrong = copy.deepcopy(export)
            wrong['files'][name]['sha256'] = 'f'*64
            with self.assertRaisesRegex(ValueError, 'adapter export hash'):
                mod.validate_adapter_exports(training, wrong)
            del wrong['files'][name]
            with self.assertRaisesRegex(ValueError, 'adapter export inventory'):
                mod.validate_adapter_exports(training, wrong)
            self.assertFalse((run.parent/name).exists())

    def test_disk_prepare_score_rebuild_and_export_hash_failure(self):
        folder, run, raw, export, proof, training = self.recovery_fixture()
        args = SimpleNamespace(command="prepare", run_dir=run, execution=ATTEMPT/"execution.json", preparation=ATTEMPT/"execution-preparation.json",
            package=PACKAGE, tokenizer=TOKENIZER, output=folder/"packets", packet_dir=None)
        self.assertTrue(mod.operate(args)["completion"]["complete"])
        self.assertEqual((args.output/'lead-only/raw/recovery.json').read_bytes(), (folder/'recovery.json').read_bytes())
        files = {f"reviewer-{r}/packet.jsonl": (args.output/f"reviewer-{r}/packet.jsonl").read_bytes() for r in mod.SEEDS}
        _, reviews = self.ratings(files)
        for r in mod.SEEDS: (args.output/f"reviewer-{r}/reviews.jsonl").write_bytes(mod.prep.lines(reviews[r]))
        args.command, args.packet_dir, args.output = "score", args.output, folder/"scored"
        self.assertFalse(mod.operate(args)["both_reviewers_screen"])
        (run/"evaluation/predictions.jsonl").write_bytes(raw["evaluation/predictions.jsonl"] + b"\n")
        args.output = folder/"tampered"
        with self.assertRaisesRegex(ValueError, "hash/size"):
            mod.operate(args)


if __name__ == "__main__":
    result = unittest.main(exit=False).result
    summary = dict(tests=result.testsRun, failures=len(result.failures), errors=len(result.errors), success=result.wasSuccessful(),
        script_sha256=mod.sha(Path(mod.__file__).read_bytes()), test_sha256=mod.sha(Path(__file__).read_bytes()),
        scorer_sha256=mod.sha(Path(mod.scoring.__file__).read_bytes()), actual_experiment_outputs_read=False)
    (SCRATCH / "test-result.json").write_bytes(mod.prep.json_bytes(summary))
    print(json.dumps(summary))
    sys.exit(not result.wasSuccessful())
