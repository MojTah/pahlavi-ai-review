"""Generated-token presence penalty for direct Transformers generation."""
from numbers import Real

import torch


class GeneratedTokenPresencePenalty:
    """Transformers LogitsProcessor callable; subtract once per generated ID.

    Set prompt_length to the initial input_ids.shape[1], including any padding.
    Pass an instance in generate(logits_processor=[...]), not presence_penalty.
    Transformers 5.13.1 merges custom processors before its sampling warpers.
    This stateless callable supports ordinary rectangular generation batches;
    each request needs its own prompt boundary. No Transformers import is needed.
    """

    supports_continuous_batching = False

    def __init__(self, prompt_length: int, penalty: float = 1.5):
        if isinstance(prompt_length, bool) or not isinstance(prompt_length, int) or prompt_length < 0:
            raise ValueError('prompt_length must be a nonnegative integer')
        if isinstance(penalty, bool) or not isinstance(penalty, Real) or not -2.0 <= penalty <= 2.0:
            raise ValueError('penalty must be a finite real number in [-2, 2]')
        self.prompt_length = prompt_length
        self.penalty = float(penalty)

    def __call__(self, input_ids: torch.Tensor, scores: torch.Tensor) -> torch.Tensor:
        if not isinstance(input_ids, torch.Tensor) or not isinstance(scores, torch.Tensor):
            raise TypeError('input_ids and scores must be tensors')
        if input_ids.ndim != 2 or scores.ndim != 2:
            raise ValueError('input_ids and scores must be rank-two tensors')
        if input_ids.shape[0] != scores.shape[0] or scores.shape[0] == 0 or scores.shape[1] == 0:
            raise ValueError('input_ids and scores need matching nonempty batches and a nonempty vocabulary')
        if input_ids.dtype != torch.int64 or not scores.is_floating_point():
            raise TypeError('input_ids must be int64 and scores must be floating point')
        if input_ids.device != scores.device:
            raise ValueError('input_ids and scores must be on the same device')
        if self.prompt_length > input_ids.shape[1]:
            raise ValueError('prompt_length exceeds the input sequence length')

        seen = torch.zeros_like(scores, dtype=torch.bool)
        # Native scatter checks generated-ID bounds without a Python GPU sync.
        # Duplicate writes all set True, so frequency never multiplies the penalty.
        seen.scatter_(1, input_ids[:, self.prompt_length:], True)
        return scores - seen.to(scores.dtype) * self.penalty
