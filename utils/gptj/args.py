from dataclasses import dataclass
from typing import List


@dataclass(init=True)
class Args:
    temperature: float = 0.9
    max_new_tokens: int = 256
    max_new_tokens_batch: int = 90
    do_sample: bool = True
    top_k: int = 50
    top_p: float = 1.0
    repetition_penalty: float = 1.0
    length_penalty: float = 1.0
    stop_sequences: List[str] = None

