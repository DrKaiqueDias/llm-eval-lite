# LLM Eval Lite

[![Python checks](https://github.com/DrKaiqueDias/llm-eval-lite/actions/workflows/tests.yml/badge.svg)](https://github.com/DrKaiqueDias/llm-eval-lite/actions)

A small Python tool for checking saved model responses against explicit rules.

In AI review, some requirements are simple enough to check automatically: a required term, a length limit or valid JSON. This project handles those checks so they can be repeated whenever a response changes. It runs locally and does not call a model.

## Try it

```sh
python evaluate.py examples/cases.jsonl
```

The bundled example deliberately includes one failure: **2 of 3 cases pass** and the command exits with status **1**. This illustrates how a quality gate catches a regression.

Each JSONL record has a unique string `id`, a string `response`, and a non-empty `rules` object:

```json
{"id":"short-answer","response":"Review required.","rules":{"contains":["review"],"excludes":["guaranteed"],"max_chars":80}}
```

| Rule | Meaning |
| --- | --- |
| `contains` | All substrings must occur, using Unicode case folding |
| `excludes` | None of the substrings may occur |
| `max_chars` | Maximum Python string length, inclusive |
| `valid_json: true` | Parse a complete JSON value, rejecting NaN and Infinity |

Exit codes: **0** all cases pass; **1** a rule fails; **2** input/configuration error. JSON goes to stdout; errors go to stderr. Blank lines are ignored; duplicate IDs and unknown rules are rejected.

## Limits

Substring checks do not understand meaning, factuality, intent or prompt injection. This tool complements human review; it is not a semantic safety evaluator. `max_chars` counts Unicode code points, not visible grapheme clusters. Reports include IDs and outcomes, not response text. Runtime is linear in the total text searched for a fixed rule set; the final report is retained in memory.

## Development

Requires **Python 3.11+**. Uses only the standard library; no installation or API keys.

```sh
python -m unittest discover -v
```

Tests run on Python 3.11, 3.12 and 3.13 through GitHub Actions. The sample data is synthetic.

## Design choices

Rules are deterministic and checked locally. The report keeps case IDs and outcomes, while response text stays out of the output. Unknown rules and duplicate IDs produce an error, rather than an incomplete evaluation.

## License

MIT. Maintained by [Kaique Dias](https://github.com/DrKaiqueDias).

