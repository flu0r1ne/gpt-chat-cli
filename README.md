gpt-chat-cli: a simple yet powerful ChatGPT CLI
-----------------------------------------------

## Introduction

`gpt-chat-cli` is a simple, general purpose ChatGPT CLI. It brings the power of ChatGPT to the command line. It aims to be easy to use and highly configurable.

Some of the features include:
- Streaming, real-time output.
- Interactive sessions with color and adornments.
- Support for any model that can be called through OpenAI's chat completions API.
  [See model endpoint compatibility.](https://platform.openai.com/docs/models/model-endpoint-compatibility)
- Ability to modify model parameters including temperature, frequency penalty, presence penalty, top p, and the maximum number of tokens emitted.
- Dynamic code syntax highlighting.
- List the available models.
- Respects Unix norms. Input can be gathered from pipes, heredoc, files, and arbitrary file descriptors.

![gpt-chat-cli Completion Demo](./assets/images/gpt.gif)

### Installation

```bash
pip install gpt-chat-cli
```

The OpenAI API uses API keys for authentication. Visit your [API Keys page](https://platform.openai.com/account/api-keys) to retrieve the API key you'll use in your requests:
```bash
export OPENAI_API_KEY="INSERT_SECRET_KEY"
```

Then, source the `OPENAI_API_KEY` environmental variable in your shell's configuration file. (That is, `~/.bashrc` or `~/.zshrc` for the Bash or Zsh shell, respectively):

```bash
source ~/.bashrc
```

### User Guide

#### Basic Usage

Without additional arguments, `gpt-chat-cli` will drop the user into an interactive shell:

```text
$ gpt-chat-cli
GPT Chat CLI version 0.1.0
Press Control-D to exit
[#] Hello!
[gpt-3.5-turbo-0301] Hello! How can I assist you today?
```

For a single completion, an initial message can be specified as the first positional argument:

```text
$ gpt-chat-cli "In one sentence, who is Joseph Weizenbaum?"
[gpt-3.5-turbo-0301] Joseph Weizenbaum was a German-American computer scientist
and philosopher who is known for creating the ELIZA program, one of the first 
natural language processing programs.
```

Alternatively, you can specify the initial message and drop into an interactive shell with `-i`:

```text
$ gpt-chat-cli -i "What linux command prints a list of all open TCP sockets on port 8080?"
GPT Chat CLI version 0.1.0
Press Control-D to exit
[#] What linux command prints a list of all open TCP sockets on port 8080?
[gpt-3.5-turbo-0301] You can use the `lsof` (list open files) command to list all
open TCP sockets on a specific port. The command to list all open TCP sockets on
port 8080 is `sudo lsof -i :8080`


[#] Can you do this with ss?
[gpt-3.5-turbo-0301] Yes, you can also use the `ss` (socket statistics) command to
list all open TCP sockets on port 8080. The command to list all open TCP sockets
on port 8080 using `ss` is `sudo ss -tlnp 'sport = :8080'`
```

`gpt-chat-cli` respects pipes and redirects, so you can use it in combination with other command-line tools:

```text
$ printf "What is smmsp in /etc/group?\n$(cat /etc/group | head)" | gpt-chat-cli
[gpt-3.5-turbo-0301] `smmsp` is a system user and group used by the Sendmail mail transfer agent (MTA)
for sending mail. The `smmsp` group is used to provide access to the Sendmail queue directory and
other Sendmail-related files. Members of this group are allowed to read and write to the Sendmail
queue directory and other Sendmail-related files.
```

```text
$ gpt-chat-cli "Write rust code to find the average of a list" > average.rs
$ cat average.rs
Here's an example Rust code to find the average of a list of numbers:

fn main() {
    let numbers = vec![1, 2, 3, 4, 5];
    let sum: i32 = numbers.iter().sum();
    let count = numbers.len();
    let average = sum / count as i32;
    println!("The average is {}", average);
}

This code creates a vector of numbers, calculates the sum of the numbers using the `iter()` method and the `sum()` method, counts the number of elements in the vector using the `len()` method, and then calculates the average by dividing the sum by the count. Finally, it prints the average to the console.
```

To list all available models, use the following command:

```text
$ gpt-chat-cli --list-models
gpt-3.5-turbo
gpt-3.5-turbo-0301
gpt-4
gpt-4-0314
gpt-4-32k
```

#### Usage

```
usage: gpt-chat-cli [-h] [-m MODEL] [-t TEMPERATURE] [-f FREQUENCY_PENALTY] [-p PRESENCE_PENALTY] [-k MAX_TOKENS] [-s TOP_P] [-n N_COMPLETIONS] [--system-message SYSTEM_MESSAGE] [--adornments {on,off,auto}]
                    [--color {on,off,auto}] [--version] [-l] [-i] [--prompt-from-fd PROMPT_FROM_FD | --prompt-from-file PROMPT_FROM_FILE]
                    [message]

positional arguments:
  message               The contents of the message. When in a interactive session, this is the initial prompt provided.

options:
  -h, --help            show this help message and exit
  -m MODEL, --model MODEL
                        ID of the model to use
  -t TEMPERATURE, --temperature TEMPERATURE
                        What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.
  -f FREQUENCY_PENALTY, --frequency-penalty FREQUENCY_PENALTY
                        Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.
  -p PRESENCE_PENALTY, --presence-penalty PRESENCE_PENALTY
                        Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.
  -k MAX_TOKENS, --max-tokens MAX_TOKENS
                        The maximum number of tokens to generate in the chat completion. Defaults to 2048.
  -s TOP_P, --top-p TOP_P
                        An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens
                        comprising the top 10% probability mass are considered.
  -n N_COMPLETIONS, --n-completions N_COMPLETIONS
                        How many chat completion choices to generate for each input message.
  --system-message SYSTEM_MESSAGE
                        Specify an alternative system message.
  --adornments {on,off,auto}
                        Show adornments to indicate the model and response. Can be set to 'on', 'off', or 'auto'.
  --color {on,off,auto}
                        Set color to 'on', 'off', or 'auto'.
  --version             Print version and exit
  -l, --list-models     List models and exit
  -i, --interactive     Start an interactive session
  --prompt-from-fd PROMPT_FROM_FD
                        Obtain the initial prompt from the specified file descriptor
  --prompt-from-file PROMPT_FROM_FILE
                        Obtain the initial prompt from the specified file
```

#### Environmental Variables

Environmental variables can control default model parameters. They are overwritten by command-line parameters if specified.

| Environmental Variable | Controls | Default Value |
| --- | --- | --- |
| `GPT_CLI_MODEL` | ID of the model to use | "gpt-3.5-turbo" |
| `GPT_CLI_TEMPERATURE` | Sampling temperature to use, between 0 and 2 | 0.5 |
| `GPT_CLI_FREQUENCY_PENALTY` | Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far | 0 |
| `GPT_CLI_PRESENCE_PENALTY` | Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far | 0 |
| `GPT_CLI_MAX_TOKENS` | The maximum number of tokens to generate in the chat completion | 2048 |
| `GPT_CLI_TOP_P` | An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with `top_p` probability mass | 1 |
| `GPT_CLI_N_COMPLETIONS` | How many chat completion choices to generate for each input message | 1 |
| `GPT_CLI_SYSTEM_MESSAGE` | Specify an alternative system message | [See this section](#system-message) |

#### System Message

The default [system message](https://platform.openai.com/docs/guides/chat/instructing-chat-models) is:

```text
The current date and time is 2023-05-06 15:55:56.619232. When emitting code or producing markdown, ensure to label fenced code blocks with the language in use.'
```

This can be overridden. GPT 3.5 sometimes forgets to emit labels for fenced code blocks, which prevents the syntax highlighting from taking effect. Thus, a reminder in the system message is recommended.

#### Tricks

You can use heredoc in `bash` to create a prompt with includes a file:

```text
$ gpt-chat-cli -i --prompt-from-fd 3 3<<EOF
heredoc> Can you review this code:
heredoc> $(cat quicksort.c)
heredoc> EOF
[#] Can you review this code:
void quicksort(struct dl_entry ** entries, int low, int high){
  if(high - low < 1)
    return;

  int left = low + 1;
  int right = high;
  while(left < right){
    if(entries[right]->access_time < entries[low]->access_time)
      right--;
...
[gpt-3.5-turbo-0301] The code appears to be a valid implementation of the quicksort algorithm for 
sorting an array of pointers to `dl_entry` structures based on the `access_time` member. However, there are a few points that could be improved:

1. Naming: The function name `quicksort` is not very descriptive. It would be better to name it something like `quicksort_entries_by_access_time` to make it clear what it does.

...
[#]
```

Create a bash alias for a particular model:

```
$ alias gpt3='gpt-chat-cli -m gpt-3.5-turbo'
$ gpt3
[#] ...
```

Of course, custom scripting can extend the capabilities. For example, this `bash` function will suggest commands to accomplish tasks on the command line:

```bash
function cmd {
	local request="$1"
	local shell=$(basename "${SHELL}")

	local os=""

	if command -v lsb_release >/dev/null 2>&1; then
		os="$ lsb_release -a\n$(lsb_release -a)\n"
	fi

	local kernel=""

	if command -v uname >/dev/null 2>&1; then
		kernel="$ uname -s -r\n$(uname -s -r)\n"
	fi

	local prompt=""

	prompt="${prompt}Suggest a command to be run in the $shell to accomplish the following task:\n\n"
	prompt="${prompt}$request\n\n"
	prompt="${prompt}Please output the command and a short description\n\n"

	if [ -n "${os}" ] || [ -n "${kernel}" ]; then
		prompt="${prompt}Here is some additional info about the system:\n\n${os}${kernel}"
	fi

	printf "$prompt" | gpt-chat-cli
}
```

```
$ cmd "test if ip forwarding is enabled"
[gpt-3.5-turbo-0301] You can use the `sysctl` command to test if IP forwarding is enabled. Here's the command you can run in your zsh shell:

sysctl net.ipv4.ip_forward

This command will return `net.ipv4.ip_forward = 0` if IP forwarding is disabled and `net.ipv4.ip_forward = 1` if IP forwarding is enabled.
```

#### Known Issues

There are a couple known issues. PRs are accepted:

1. `gpt-chat-cli` lacks shell completion
2. `gpt-chat-cli` does not track token usage. Ideally, it should gracefully handle long messages and remove messages from the chat history if the number of tokens in the context is exceeded. If the tokens exceed the model's context, the following error will occur:

```text
openai.error.InvalidRequestError: This model's maximum context length is 4097 tokens. However, your messages resulted in 9758 tokens. Please reduce the length of the messages.
```

