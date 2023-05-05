#!/bin/env python3

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
    Arguments,
    DisplayArguments,
    CompletionArguments,
)

from .color import get_color_codes

###########################
####   SAVE / REPLAY   ####
###########################

def create_chat_completion_from_args(args : CompletionArguments) \
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

def save_response_and_arguments(args : Arguments) -> None:
    completion = create_chat_completion_from_args(args.completion_args)
    completion = list(completion)

    filename = args.debug_args.save_response_to_file

    with open(filename, 'wb') as f:
        pickle.dump((args.completion_args, completion,), f)

def load_response_and_arguments(args : Arguments) \
        -> Tuple[CompletionArguments, OpenAIChatResponseStream]:

    filename = args.debug_args.load_response_from_file

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

def print_streamed_response(
        display_args : DisplayArguments,
        completion : OpenAIChatResponseStream,
        n_completions : int
    ) -> None:
    """
    Print the response in real time by printing the deltas as they occur. If multiple responses
    are requested, print the first in real-time, accumulating the others in the background. One the
    first response completes, move on to the second response printing the deltas in real time. Continue
    on until all responses have been printed.
    """

    COLOR_CODE = get_color_codes(no_color = not display_args.color)
    adornments = display_args.adornments

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

        if not prompt_printed and adornments:
            res_indicator = '' if n_completions == 1 else \
                    f' {display_idx + 1}/{n_completions}'
            PROMPT = f'[{COLOR_CODE.GREEN}{update.model}{COLOR_CODE.RESET}{COLOR_CODE.RED}{res_indicator}{COLOR_CODE.RESET}]'
            prompt_printed = True
            print(PROMPT, end=' ', flush=True)


        content = display_response.take_content()
        print(f'{COLOR_CODE.WHITE}{content}{COLOR_CODE.RESET}',
              sep='', end='', flush=True)

        if display_response.finish_reason is not FinishReason.NONE:
            if display_idx < n_completions:
                display_idx += 1
                prompt_printed = False

            if adornments:
                print(end='\n\n', flush=True)
            else:
                print(end='\n', flush=True)

def main():
    args = parse_args()

    completion_args = args.completion_args

    if args.debug_args:
        debug_args : DebugArguments = args.debug_args

        if debug_args.save_response_to_file:
            save_response_and_arguments(args)
            return
        elif debug_args.load_response_from_file:
            completion_args, completion = load_response_and_arguments(args)
    else:
        completion = create_chat_completion_from_args(completion_args)

    print_streamed_response(
        args.display_args,
        completion,
        completion_args.n_completions
    )

if __name__ == "__main__":
    main()
