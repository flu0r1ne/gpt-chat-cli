gpt-chat-cli
------------

A simple ChatGPT CLI.

### Installation:

```
pip install gpt-chat-cli
```

The OpenAI API uses API keys for authentication. Visit your (API Keys page)[https://platform.openai.com/account/api-keys] to retrieve the API key you'll use in your requests. Then, source the `OPENAI_API_KEY` environmental variable in your shell's configuration file. (That is, `~/.bashrc` or `~/.zshrc` for the Bash or Zsh shell, respectively.)
```
export OPENAI_API_KEY="INSERT_SECRET_KEY"
```

### Examples:

```
[#] gpt-chat-cli "Tell me about Joseph Weizenbaum"

[gpt-3.5-turbo-0301] Joseph Weizenbaum (1923-2008) was a German-American computer scientist and philosopher who is best known for creating the ELIZA program, one of the earliest examples of natural language processing. ELIZA was a computer program that simulated a psychotherapist and could engage in a conversation with a human user by using simple pattern-matching techniques to respond to the user's input.

Weizenbaum was born in Berlin, Germany, and fled the country with his family in 1936 to escape Nazi persecution. He later studied mathematics and physics at Wayne State University in Detroit, Michigan, and received a Ph.D. in computer science from the Massachusetts Institute of Technology (MIT) in 1956.

In addition to his work on ELIZA, Weizenbaum was also a prominent critic of artificial intelligence and the use of computers in society. He argued that computers could not truly understand human language or emotions, and that the increasing reliance on technology could lead to dehumanization and loss of personal autonomy.

Weizenbaum's writings and lectures on the social and ethical implications of technology have had a lasting impact on the field of computer science and continue to be studied and debated today.
```

```
[#] gpt-chat-cli -n 2 "Write Rust code to find the variance of a list of floating point numbers"
[gpt-3.5-turbo-0301 1/2] Here's the Rust code to find the variance of a list of floating point numbers:

fn variance(numbers: &[f64]) -> Option<f64> {
    let n = numbers.len() as f64;
    if n <= 1.0 {
        return None;
    }
    let mean = numbers.iter().sum::<f64>() / n;
    let variance = numbers.iter().map(|x| (x - mean).powi(2)).sum::<f64>() / (n - 1.0);
    Some(variance)
}

This function takes a slice of floating point numbers as input and returns an `Option<f64>` which is the variance of the numbers. If the length of the slice is less than or equal to 1, the function returns `None` since variance cannot be calculated for such cases.

The function calculates the mean of the numbers by summing up all the numbers and dividing by the length of the slice. It then calculates the variance by iterating over the numbers, subtracting the mean from each number, squaring the result and summing up all the squares. Finally, it divides the sum of squares by (n-1) to get the variance.

Note that we use `powi(2)` instead of `powf(2.0)` to avoid floating point errors.

[gpt-3.5-turbo-0301 2/2] Here's one possible implementation:

fn variance(data: &[f64]) -> Option<f64> {
    let n = data.len() as f64;
    if n <= 1.0 {
        return None; // need at least 2 data points
    }
    let mean = data.iter().sum::<f64>() / n;
    let variance = data.iter().map(|x| (x - mean).powi(2)).sum::<f64>() / (n - 1.0);
    Some(variance)
}

This function takes a slice of `f64` values as input, and returns an `Option<f64>` which is `None` if the input slice has fewer than 2 elements (since we need at least 2 data points to compute a variance), or the computed variance otherwise.

The variance is computed using the formula:

variance = sum((x - mean)^2) / (n - 1)

where `x` is each data point, `mean` is the mean of the data, `n` is the number of data points, and `^2` means "squared". The `map()` method is used to compute the squared differences `(x - mean)^2`, and the `sum()` method is used to add them up. Finally, the result is divided by `n - 1` to get the unbiased sample variance (which is what we usually want).

Note that this implementation uses the `powi()` method to compute the squared differences, which is faster than using the `powf()` method with a constant exponent of 2.
```

### Usage:

```
usage: gpt-chat-cli [-h] [-m MODEL] [-t TEMPERATURE] [-f FREQUENCY_PENALTY] [-p PRESENCE_PENALTY] [-k MAX_TOKENS] [-s TOP_P] [-n N_COMPLETIONS]
                    [--adornments {AutoDetectedOption.ON,AutoDetectedOption.OFF,AutoDetectedOption.AUTO}] [--color {AutoDetectedOption.ON,AutoDetectedOption.OFF,AutoDetectedOption.AUTO}]
                    message

positional arguments:
  message               The contents of the message. When used in chat mode, this is the initial message if provided.

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
  --adornments {AutoDetectedOption.ON,AutoDetectedOption.OFF,AutoDetectedOption.AUTO}
                        Show adornments to indicate the model and response. Can be set to 'on', 'off', or 'auto'.
  --color {AutoDetectedOption.ON,AutoDetectedOption.OFF,AutoDetectedOption.AUTO}
                        Set color to 'on', 'off', or 'auto'.
```

### Features:

- [x] Streaming real-time output
- [x] Color and adornments
- [x] Support for multiple completions
- [x] Support for any model which is supported through the chat completions API. [See model endpoint compatibility.](https://platform.openai.com/docs/models/model-endpoint-compatibility)
- [x] Capability to modify parameters including temperature, frequency penalty, presence penalty, top p, and the maximum number of tokens emitted.

> This is a WIP.
