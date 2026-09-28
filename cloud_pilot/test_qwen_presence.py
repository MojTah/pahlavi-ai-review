"""Real CPU tensor checks; no checkpoint, GPU, or Transformers import required."""
import unittest

import torch

from .qwen_presence import GeneratedTokenPresencePenalty


class PresencePenaltyTests(unittest.TestCase):
    def test_prompt_exclusion_repeats_and_batch_independence(self):
        processor = GeneratedTokenPresencePenalty(prompt_length=2)
        ids = torch.tensor([[0, 1, 2, 2, 2], [2, 3, 1, 1, 3]])
        scores = torch.tensor([[4., 3., 2., 1.], [4., 3., 2., 1.]])
        original = scores.clone()
        actual = processor(ids, scores)
        torch.testing.assert_close(actual, torch.tensor([[4., 3., .5, 1.], [4., 1.5, 2., -.5]]))
        torch.testing.assert_close(scores, original)
        torch.testing.assert_close(processor(ids.flip(0), scores), actual.flip(0))

    def test_empty_suffix_and_fresh_request(self):
        processor = GeneratedTokenPresencePenalty(2)
        scores = torch.zeros(1, 4)
        processor(torch.tensor([[0, 1, 2]]), scores)
        torch.testing.assert_close(processor(torch.tensor([[2, 3]]), scores), scores)
        torch.testing.assert_close(
            GeneratedTokenPresencePenalty(0)(torch.empty((1, 0), dtype=torch.int64), scores), scores)
        torch.testing.assert_close(
            processor(torch.tensor([[2, 3, 0]]), scores), torch.tensor([[-1.5, 0., 0., 0.]]))

    def test_distribution_ranking_and_temperature_order(self):
        ids = torch.tensor([[3, 0]])
        scores = torch.tensor([[2., 1., 0., -1.]])
        processor = GeneratedTokenPresencePenalty(1)
        adjusted = processor(ids, scores)
        self.assertEqual(scores.argmax().item(), 0)
        self.assertEqual(adjusted.argmax().item(), 1)
        self.assertLess(adjusted.softmax(-1)[0, 0], scores.softmax(-1)[0, 0])
        # Apply the additive penalty before temperature; reversing this changes it.
        probabilities = (adjusted / .7).softmax(-1)
        expected = (torch.tensor([[.5, 1., 0., -1.]]) / .7).softmax(-1)
        torch.testing.assert_close(probabilities, expected)
        self.assertFalse(torch.allclose(probabilities, processor(ids, scores / .7).softmax(-1)))
        self.assertEqual(adjusted.topk(1).indices.item(), 1)

    def test_dtype_masking_and_valid_penalty_endpoints(self):
        for dtype in (torch.float16, torch.bfloat16, torch.float32, torch.float64):
            scores = torch.tensor([[0., 2., float('-inf')]], dtype=dtype)
            for penalty in (-2., 0., 1.5, 2.):
                with self.subTest(dtype=dtype, penalty=penalty):
                    actual = GeneratedTokenPresencePenalty(0, penalty)(torch.tensor([[1, 1]]), scores)
                    self.assertEqual(actual.dtype, dtype)
                    torch.testing.assert_close(actual, torch.tensor([[0., 2. - penalty, float('-inf')]], dtype=dtype))

    def test_constructor_rejects_invalid_values(self):
        for boundary in (True, -1, 1.5, float('inf'), float('nan'), '2', None):
            with self.subTest(boundary=boundary), self.assertRaises(ValueError):
                GeneratedTokenPresencePenalty(boundary)
        for penalty in (True, -2.01, 2.01, float('inf'), float('-inf'), float('nan'), '1.5', None):
            with self.subTest(penalty=penalty), self.assertRaises(ValueError):
                GeneratedTokenPresencePenalty(0, penalty)

    def test_tensor_boundary_shape_dtype_device_and_token_validation(self):
        processor = GeneratedTokenPresencePenalty(1)
        valid_ids, valid_scores = torch.tensor([[0, 1]]), torch.zeros(1, 3)
        invalid = [
            ([0, 1], valid_scores, TypeError),
            (valid_ids, [[0., 0., 0.]], TypeError),
            (valid_ids[0], valid_scores, ValueError),
            (valid_ids, valid_scores[0], ValueError),
            (valid_ids, torch.zeros(2, 3), ValueError),
            (valid_ids[:0], valid_scores[:0], ValueError),
            (valid_ids, torch.zeros(1, 0), ValueError),
            (valid_ids[:, :0], valid_scores, ValueError),
            (valid_ids.float(), valid_scores, TypeError),
            (valid_ids.int(), valid_scores, TypeError),
            (valid_ids, valid_scores.long(), TypeError),
            (valid_ids, torch.empty(1, 3, device='meta'), ValueError),
            (torch.tensor([[0, -1]]), valid_scores, RuntimeError),
            (torch.tensor([[0, 3]]), valid_scores, RuntimeError),
        ]
        for ids, scores, error in invalid:
            with self.subTest(ids=ids, scores=scores), self.assertRaises(error):
                processor(ids, scores)


if __name__ == '__main__':
    unittest.main()
