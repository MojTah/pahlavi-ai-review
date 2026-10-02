"""Offline fresh-run handoff checks; no approvals or provider requests."""
import json
from pathlib import Path
import socket
import unittest
import uuid
from unittest.mock import patch

import prepare_execution as handoff


class HandoffChecks(unittest.TestCase):
    def test_real_preparation_sdk_no_network_and_reused_folder(self):
        from huggingface_hub import HfApi
        from huggingface_hub.hf_api import _create_job_spec
        packet = handoff.reviewed.PACKET
        before = {p.name: p.read_bytes() for p in packet.iterdir() if p.is_file()}
        destination = handoff.reviewed.ROOT / 'resources/local/execution-handoff-tests' / uuid.uuid4().hex
        run_id = uuid.uuid4().hex
        with patch.object(socket.socket, 'connect', side_effect=AssertionError('No network')), \
                patch.object(socket, 'create_connection', side_effect=AssertionError('No network')), \
                patch.object(HfApi, '__init__', side_effect=AssertionError('No API client')), \
                patch('huggingface_hub.hf_api._create_job_spec', wraps=_create_job_spec) as serializer:
            self.assertEqual(handoff.prepare(run_id=run_id, out=destination), destination)
            self.assertGreater(serializer.call_count, 0)
            inventory = json.loads((destination / 'handoff.json').read_bytes())
            self.assertEqual(inventory['status'], 'NOT_SUBMITTED')
            self.assertEqual(inventory['authorization_status'], 'NOT_AUTHORIZED')
            self.assertTrue(inventory['sdk_serialization_passed'])
            self.assertEqual(len(inventory['transfer_inventory']), 2)
            self.assertIn('references.jsonl', inventory['excluded_from_transfer'])
            self.assertEqual({p.name for p in destination.iterdir()},
                {'job-spec.json', 'job-receipt.json', 'handoff.json', inventory['transfer_inventory'][0]['remote_path'].split('/')[-1]})
            original = {p.name: p.read_bytes() for p in destination.iterdir()}
            with self.assertRaises(FileExistsError): handoff.prepare(run_id=run_id, out=destination)
            self.assertEqual(original, {p.name: p.read_bytes() for p in destination.iterdir()})
        self.assertEqual(before, {p.name: p.read_bytes() for p in packet.iterdir() if p.is_file()})

    def test_unexpected_equivalence_mutation_rejected_before_write(self):
        from cloud_pilot import hf_learning_eval
        destination = handoff.reviewed.ROOT / 'resources/local/execution-handoff-tests' / uuid.uuid4().hex
        original_prepare = hf_learning_eval.prepare
        def changed(*args, **kwargs):
            spec, receipt = original_prepare(*args, **kwargs)
            # The fixed reviewed reconstruction is still checked without mutation.
            if args[1] != handoff.reviewed.RUN_ID:
                spec['timeout'] = '119m'
            return spec, receipt
        with patch.object(hf_learning_eval, 'prepare', side_effect=changed):
            with self.assertRaisesRegex(ValueError, 'SDK specification differs'):
                handoff.prepare(out=destination)
        self.assertFalse(destination.exists())

    def test_missing_or_changed_reviewed_bytes_rejected_before_write(self):
        original_read = Path.read_bytes
        destination = handoff.reviewed.ROOT / 'resources/local/execution-handoff-tests' / uuid.uuid4().hex
        for missing in (False, True):
            def changed(path):
                if path == handoff.reviewed.HERE / 'runtime-check.json':
                    if missing:
                        raise FileNotFoundError('missing reviewed bytes')
                    return b'{}'
                return original_read(path)
            with self.subTest(missing=missing), patch.object(Path, 'read_bytes', changed):
                with self.assertRaises((ValueError, FileNotFoundError)): handoff.prepare(out=destination)
            self.assertFalse(destination.exists())


if __name__ == '__main__':
    unittest.main()
