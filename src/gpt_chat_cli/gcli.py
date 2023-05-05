#!/bin/env python3

import sys
import openai
import pickle

from collections import defaultdict
from dataclasses import dataclass
from typing import Tuple

from .openai_wrappers import (
    create_chat_completion,
    list_models,
    OpenAIChatResponse,
    OpenAIChatResponseStream,
    FinishReason,
    Role,
    ChatMessage
)

from .argparsing import (
    parse_args,
    Arguments,
    DisplayArguments,
    CompletionArguments,
    DebugArguments,
)

from .version import VERSION
from .color import get_color_codes

###########################
####   SAVE / REPLAY   ####
###########################

def create_singleton_chat_completion(
        message : str,
        completion_args : CompletionArguments
    ):

    hist = [ ChatMessage( Role.USER, message ) ]

    completion = create_chat_completion(hist, completion_args)

    return completion

def save_response_and_arguments(args : Arguments) -> None:

    message = args.initial_message

    completion = create_singleton_chat_completion(message, args.completion_args)
    completion = list(completion)

    filename = args.debug_args.save_response_to_file

    with open(filename, 'wb') as f:
        pickle.dump((message, args.completion_args, completion,), f)

def load_response_and_arguments(args : Arguments) \
        -> Tuple[CompletionArguments, OpenAIChatResponseStream]:

    filename = args.debug_args.load_response_from_file

    with open(filename, 'rb') as f:
        message, args, completion = pickle.load(f)

    return (message, args, completion)

#########################
#### PRETTY PRINTING ####
#########################

@dataclass
class CumulativeResponse:
    delta_content: str = ""
    finish_reason: FinishReason = FinishReason.NONE
    content: str = ""

    def take_delta(self : "CumulativeResponse"):
        chunk = self.delta_content
        self.delta_content = ""
        return chunk

    def add_content(self : "CumulativeResponse", new_chunk : str):
        self.content += new_chunk
        self.delta_content += new_chunk

def print_streamed_response(
        display_args : DisplayArguments,
        completion : OpenAIChatResponseStream,
        n_completions : int,
        return_responses : bool = False
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
                cumu_responses[choice.index].add_content(delta.content)

            if choice.finish_reason is not FinishReason.NONE:
                cumu_responses[choice.index].finish_reason = choice.finish_reason

        display_response = cumu_responses[display_idx]

        if not prompt_printed and adornments:
            res_indicator = '' if n_completions == 1 else \
                    f' {display_idx + 1}/{n_completions}'
            PROMPT = f'[{COLOR_CODE.GREEN}{update.model}{COLOR_CODE.RESET}{COLOR_CODE.RED}{res_indicator}{COLOR_CODE.RESET}]'
            prompt_printed = True
            print(PROMPT, end=' ', flush=True)


        content = display_response.take_delta()
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

    if return_responses:
        return [ cumu_responses[i].content for i in range(n_completions) ]

def cmd_version():
    print(f'version {VERSION}')

def cmd_list_models():
    for model in list_models():
        print(model)

def cmd_interactive(args : Arguments):
    COLOR_CODE = get_color_codes(no_color = not args.display_args.color)

    completion_args = args.completion_args
    display_args = args.display_args

    hist = []

    def print_prompt():

        print(f'[{COLOR_CODE.WHITE}#{COLOR_CODE.RESET}]', end=' ', flush=True)

    def prompt_message() -> bool:
        print_prompt()

        # Control-D closes the input stream
        try:
            message = input()
        except EOFError:
            print()
            return False

        hist.append( ChatMessage( Role.USER, message ) )

        return True

    print(f'GPT Chat CLI version {VERSION}')
    print(f'Press Control-D to exit')

    if args.initial_message:
        print_prompt()
        print( args.initial_message )
        hist.append( ChatMessage( Role.USER, args.initial_message ) )
    else:
        prompt_message()

    while True:

        completion = create_chat_completion(hist, completion_args)

        response = print_streamed_response(
            display_args, completion, 1, return_responses=True,
        )[0]

        hist.append( ChatMessage(Role.ASSISTANT, response) )

        if not prompt_message():
            break

def cmd_singleton(args: Arguments):
    completion_args = args.completion_args

    debug_args : DebugArguments = args.debug_args
    message = args.initial_message

    if debug_args.save_response_to_file:
        save_response_and_arguments(args)
        return
    elif debug_args.load_response_from_file:
        message, completion_args, completion = load_response_and_arguments(args)
    else:
        # message is only None is a TTY is not attached
        if message is None:
            message = sys.stdin.read()

        completion = create_singleton_chat_completion(message, completion_args)

    print_streamed_response(
        args.display_args,
        completion,
        completion_args.n_completions
    )


def main():
    args = parse_args()

    if args.version:
        cmd_version()
    elif args.list_models:
        cmd_list_models()
    elif args.interactive:
        cmd_interactive(args)
    else:
        cmd_singleton(args)

if __name__ == "__main__":
    main()
