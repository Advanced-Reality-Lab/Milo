from typing import Dict, Set, List

import gc
import torch
from transformers import GPTJForCausalLM, GPT2TokenizerFast

from utils.gptj.args import Args
import time


def generate(model: GPTJForCausalLM,
             tokenizer: GPT2TokenizerFast,
             batch_sentences: List[str],
             args: Args = Args(),
             inference_batch_size: int = 20,
             verbose: bool = True) -> List[str]:

    if isinstance(batch_sentences, tr):
        batch_sentences = [batch_sentences]
    if args.stop_sequences is None:
        args.stop_sequences = []
    if not args.stop_sequences.__contains__('<|endoftext|>'):
        args.stop_sequences.append('<|endoftext|>')
    if not args.stop_sequences.__contains__('Therapist:'):
        args.stop_sequences.append('Therapist:')

    tokenizer.padding_side = 'right'
    tokenizer.pad_token = model.config.eos_token_id

    if model.config.pad_token_id is None:
        model.config.pad_token_id = model.config.eos_token_id

    batches = [batch_sentences[idx:idx + inference_batch_size] for idx in
               range(0, len(batch_sentences), inference_batch_size)]
    results = []
    i, j = 1, 0
    for b in batches:
        if verbose:
            print(f'{i}/{len(batches)}')
            i += 1
        batch = {k: b[k] for k in range(len(b))}

        _generate(model=model,
                  tokenizer=tokenizer,
                  prompts=batch,
                  args=args)

        for k in range(len(b)):
            results.append(batch[k][len(batch_sentences[j]):].strip())
            j += 1

    torch.cuda.empty_cache()
    gc.collect()

    return results


def _generate(model: GPTJForCausalLM,
              tokenizer: GPT2TokenizerFast,
              prompts: Dict[int, str] = None,
              prompts_initial_len: Dict[int, int] = None,
              generate_prompts_keys: Set[int] = None,
              args: Args = None):
    if not prompts_initial_len:
        prompts_initial_len = {k: len(prompts[k]) for k in prompts.keys()}

    key_min, key_max = min(prompts.keys()), max(prompts.keys())
    if not generate_prompts_keys:
        generate_prompts_keys: Set[int] = set()
        for k in range(key_min, key_max + 1):
            generate_prompts_keys.add(k)

    list_prompts = [prompts[k] for k in generate_prompts_keys]

    input_ids = tokenizer(list_prompts,
                          padding=True,
                          return_tensors="pt").input_ids.to(f'cuda:{model.device.index}')
    with torch.no_grad():
        gen_tokens: torch.Tensor = model.generate(input_ids=input_ids,
                                                  do_sample=args.do_sample,
                                                  temperature=args.temperature,
                                                  max_new_tokens=args.max_new_tokens_batch)


    prompts_len = {k: len(prompts[k]) for k in generate_prompts_keys}
    decoded = tokenizer.batch_decode(gen_tokens)

    for i in range(len(decoded)):
        while decoded[i].startswith('<|endoftext|>'):
            decoded[i] = decoded[i][13:]

    generate_prompts_keys_new = generate_prompts_keys.copy()
    for k, i in zip(generate_prompts_keys, range(len(decoded))):
        prompts[k] = decoded[i]

        start_searching = prompts_initial_len[k] + args.max_new_tokens
        indices = [prompts[k].find(stop_seq, prompts_len[k]) for stop_seq in args.stop_sequences]
        indices += [prompts[k].find(stop_seq, start_searching) for stop_seq in ['.', '!', '?']]
        indices = list(filter(lambda x: x > -1, indices))

        if len(indices) == 0:
            if len(prompts[k]) - prompts_initial_len[k] < args.max_new_tokens:
                continue
        else:
            min_index = min(indices)
            if prompts[k][min_index] in ['.', '!', '?']:
                min_index += 1
            prompts[k] = prompts[k][:min_index].strip()

        if prompts[k].endswith('\\n'):
            prompts[k] = prompts[k][:-2].strip()

        generate_prompts_keys_new.remove(k)

    if len(generate_prompts_keys_new) > 0:
        _generate(model=model,
                  tokenizer=tokenizer,
                  prompts=prompts,
                  prompts_initial_len=prompts_initial_len,
                  generate_prompts_keys=generate_prompts_keys_new,
                  args=args)
