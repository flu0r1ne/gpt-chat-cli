import argparse
import os
import logging
import openai
import sys
from enum import Enum
from dataclasses import dataclass
from typing import Tuple, Optional

class AutoDetectedOption(Enum):
    ON = 'on'
    OFF = 'off'
    AUTO = 'auto'

    def __str__(self : "AutoDetectedOption"):
        return self.value

def die_validation_err(err : str):
    print(err, file=sys.stderr)
    sys.exit(1)

def validate_args(args: argparse.Namespace) -> None:
    if not 0 <= args.temperature <= 2:
        die_validation_err("Temperature must be between 0 and 2.")

    if not -2 <= args.frequency_penalty <= 2:
        die_validation_err("Frequency penalty must be between -2.0 and 2.0.")

    if not -2 <= args.presence_penalty <= 2:
        die_validation_err("Presence penalty must be between -2.0 and 2.0.")

    if args.max_tokens < 1:
        die_validation_err("Max tokens must be greater than or equal to 1.")

    if not 0 <= args.top_p <= 1:
        die_validation_err("Top_p must be between 0 and 1.")

    if args.n_completions < 1:
        die_validation_err("Number of completions must be greater than or equal to 1.")

@dataclass
class CompletionArguments:
    model: str
    n_completions: int
    temperature: float
    presence_penalty: float
    frequency_penalty: float
    max_tokens: int
    top_p: float
    message: str

@dataclass
class DisplayArguments:
    adornments: bool
    color: bool


@dataclass
class DebugArguments:
    save_response_to_file: Optional[str]
    load_response_from_file: Optional[str]

@dataclass
class Arguments:
    completion_args: CompletionArguments
    display_args: DisplayArguments
    version: bool
    debug_args: Optional[DebugArguments] = None

def split_arguments(args: argparse.Namespace) -> Arguments:
    completion_args = CompletionArguments(
        model=args.model,
        n_completions=args.n_completions,
        temperature=args.temperature,
        presence_penalty=args.presence_penalty,
        frequency_penalty=args.frequency_penalty,
        max_tokens=args.max_tokens,
        top_p=args.top_p,
        message=args.message
    )

    display_args = DisplayArguments(
        adornments=(args.adornments == AutoDetectedOption.ON),
        color=(args.color == AutoDetectedOption.ON),
    )

    debug_args = DebugArguments(
        save_response_to_file=args.save_response_to_file,
        load_response_from_file=args.load_response_from_file,
    )

    return Arguments(
           completion_args=completion_args,
           display_args=display_args,
           debug_args=debug_args,
           version=args.version
    )

def parse_args() -> Arguments:

    GCLI_ENV_PREFIX = "GCLI_"

    debug = os.getenv(f'{GCLI_ENV_PREFIX}DEBUG') is not None

    if debug:
        logging.warning("Debugging mode and unstable features have been enabled.")

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-m",
        "--model",
        default=os.getenv(f'{GCLI_ENV_PREFIX}MODEL', "gpt-3.5-turbo"),
        help="ID of the model to use",
    )

    parser.add_argument(
        "-t",
        "--temperature",
        type=float,
        default=os.getenv(f'{GCLI_ENV_PREFIX}TEMPERATURE', 0.5),
        help=(
            "What sampling temperature to use, between 0 and 2. Higher values "
            "like 0.8 will make the output more random, while lower values "
            "like 0.2 will make it more focused and deterministic."
        ),
    )

    parser.add_argument(
        "-f",
        "--frequency-penalty",
        type=float,
        default=os.getenv(f'{GCLI_ENV_PREFIX}FREQUENCY_PENALTY', 0),
        help=(
            "Number between -2.0 and 2.0. Positive values penalize new tokens based "
            "on their existing frequency in the text so far, decreasing the model's "
            "likelihood to repeat the same line verbatim."
        ),
    )

    parser.add_argument(
        "-p",
        "--presence-penalty",
        type=float,
        default=os.getenv(f'{GCLI_ENV_PREFIX}PRESENCE_PENALTY', 0),
        help=(
            "Number between -2.0 and 2.0. Positive values penalize new tokens based "
            "on whether they appear in the text so far, increasing the model's "
            "likelihood to talk about new topics."
        ),
    )

    parser.add_argument(
        "-k",
        "--max-tokens",
        type=int,
        default=os.getenv(f'{GCLI_ENV_PREFIX}MAX_TOKENS', 2048),
        help=(
            "The maximum number of tokens to generate in the chat completion. "
            "Defaults to 2048."
        ),
    )

    parser.add_argument(
        "-s",
        "--top-p",
        type=float,
        default=os.getenv(f'{GCLI_ENV_PREFIX}TOP_P', 1),
        help=(
            "An alternative to sampling with temperature, called nucleus sampling, "
            "where the model considers the results of the tokens with top_p "
            "probability mass. So 0.1 means only the tokens comprising the top 10%% "
            "probability mass are considered."
        ),
    )

    parser.add_argument(
        "-n",
        "--n-completions",
        type=int,
        default=os.getenv('f{GCLI_ENV_PREFIX}N_COMPLETIONS', 1),
        help="How many chat completion choices to generate for each input message.",
    )

    parser.add_argument(
        "--adornments",
        type=AutoDetectedOption,
        choices=list(AutoDetectedOption),
        default=AutoDetectedOption.AUTO,
        help=(
            "Show adornments to indicate the model and response."
            " Can be set to 'on', 'off', or 'auto'."
        )
    )

    parser.add_argument(
        "--color",
        type=AutoDetectedOption,
        choices=list(AutoDetectedOption),
        default=AutoDetectedOption.AUTO,
        help="Set color to 'on', 'off', or 'auto'.",
    )

    parser.add_argument(
        "--version",
        # type=bool,
        action="store_true",
        help="Print version and exit"
    )

    parser.add_argument(
        "message",
        type=str,
        nargs='?',
        help=(
            "The contents of the message. When used in chat mode, this is the initial "
            "message if provided."
        ),
    )

    if debug:
        group = parser.add_mutually_exclusive_group()

        group.add_argument(
            '--save-response-to-file',
            type=str,
            help="UNSTABLE: save the response to a file. This can reply a response for debugging purposes",
        )

        group.add_argument(
            '--load-response-from-file',
            type=str,
            help="UNSTABLE: load a response from a file. This can reply a response for debugging purposes",
        )

    openai_key = os.getenv("OPENAI_KEY", os.getenv("OPENAI_API_KEY"))
    if not openai_key:
        print("The OPENAI_API_KEY or OPENAI_KEY environment variable must be defined.", file=sys.stderr)
        print("The OpenAI API uses API keys for authentication. Visit your (API Keys page)[https://platform.openai.com/account/api-keys] to retrieve the API key you'll use in your requests.", file=sys.stderr)
        sys.exit(1)

    openai.api_key = openai_key

    args = parser.parse_args()

    if debug and args.load_response_from_file:
        logging.warning(f'Ignoring the provided arguments in favor of those provided when the response in {args.load_response_from_file} was generated')

    if args.color == AutoDetectedOption.AUTO:
        if os.getenv("NO_COLOR"):
            args.color = AutoDetectedOption.OFF
        elif sys.stdout.isatty():
            args.color = AutoDetectedOption.ON
        else:
            args.color = AutoDetectedOption.OFF

    if args.adornments == AutoDetectedOption.AUTO:
        if sys.stdout.isatty():
            args.adornments = AutoDetectedOption.ON
        else:
            args.adornments = AutoDetectedOption.OFF

    if not debug:
        args.load_response_from_file = None
        args.save_response_to_file = None

    validate_args(args)

    return split_arguments(args)
