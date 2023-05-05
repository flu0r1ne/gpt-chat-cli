#!/bin/env python3

import argparse
import sys
import openai
import pickle

from collections import defaultdict
from dataclasses import dataclass
from typing import Tuple

from .openai_wrappers import (
    create_chat_completion,
    OpenAIChatResponse,
    OpenAIChatResponseStream,
    FinishReason,
)

from .argparsing import (
    parse_args,
    AutoDetectedOption,
)

from .color import get_color_codes

###########################
####   SAVE / REPLAY   ####
###########################

def create_chat_completion_from_args(args : argparse.Namespace) \
        -> OpenAIChatResponseStream:
    return create_chat_completion(
        model=args.model,
        messages=[{ "role": "user", "content": args.message }],
        n=args.n_completions,
        temperature=args.temperature,
        presence_penalty=args.presence_penalty,
        frequency_penalty=args.frequency_penalty,
        max_tokens=args.max_tokens,
        top_p=args.top_p,
        stream=True
    )

def save_response_and_arguments(args : argparse.Namespace) -> None:
    completion = create_chat_completion_from_args(args)
    completion = list(completion)

    filename = args.save_response_to_file

    with open(filename, 'wb') as f:
        pickle.dump((args, completion,), f)

def load_response_and_arguments(args : argparse.Namespace) \
        -> Tuple[argparse.Namespace, OpenAIChatResponseStream]:

    filename = args.load_response_from_file

    with open(filename, 'rb') as f:
        args, completion = pickle.load(f)

    return (args, completion)

#########################
#### PRETTY PRINTING ####
#########################

@dataclass
class CumulativeResponse:
    content: str = ""
    finish_reason: FinishReason = FinishReason.NONE

    def take_content(self : "CumulativeResponse"):
        chunk = self.content
        self.content = ""
        return chunk

def print_streamed_response(args : argparse.Namespace, completion : OpenAIChatResponseStream):
    """
    Print the response in real time by printing the deltas as they occur. If multiple responses
    are requested, print the first in real-time, accumulating the others in the background. One the
    first response completes, move on to the second response printing the deltas in real time. Continue
    on until all responses have been printed.
    """

    COLOR_CODE = get_color_codes(no_color = args.color == AutoDetectedOption.OFF)
    ADORNMENTS = args.adornments == AutoDetectedOption.ON
    N_COMPLETIONS = args.n_completions

    cumu_responses = defaultdict(CumulativeResponse)
    display_idx = 0
    prompt_printed = False

    for update in completion:

        for choice in update.choices:
            delta = choice.delta

            if delta.content:
                cumu_responses[choice.index].content += delta.content

            if choice.finish_reason is not FinishReason.NONE:
                cumu_responses[choice.index].finish_reason = choice.finish_reason

        display_response = cumu_responses[display_idx]

        if not prompt_printed and ADORNMENTS:
            res_indicator = '' if N_COMPLETIONS == 1 else \
                    f' {display_idx + 1}/{n_completions}'
            PROMPT = f'[{COLOR_CODE.GREEN}{update.model}{COLOR_CODE.RESET}{COLOR_CODE.RED}{res_indicator}{COLOR_CODE.RESET}]'
            prompt_printed = True
            print(PROMPT, end=' ', flush=True)


        content = display_response.take_content()
        print(f'{COLOR_CODE.WHITE}{content}{COLOR_CODE.RESET}',
              sep='', end='', flush=True)

        if display_response.finish_reason is not FinishReason.NONE:
            if display_idx < N_COMPLETIONS:
                display_idx += 1
                prompt_printed = False

            if ADORNMENTS:
                print(end='\n\n', flush=True)
            else:
                print(end='\n', flush=True)

def main():
    args = parse_args()

    if args.save_response_to_file:
        save_response_and_arguments(args)
        return
    elif args.load_response_from_file:
        args, completion = load_response_and_arguments(args)
    else:
        completion = create_chat_completion_from_args(args)

    print_streamed_response(args, completion)

if __name__ == "__main__":
    main()
