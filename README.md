# LLM Eval Lite

[![Python checks](https://github.com/DrKaiqueDias/llm-eval-lite/actions/workflows/tests.yml/badge.svg)](https://github.com/DrKaiqueDias/llm-eval-lite/actions)

An offline regression-checking CLI for model responses. Turn simple output requirements into repeatable checks without calling a model or sending data to a service.

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

CI runs tests on Python 3.11, 3.12 and 3.13. Examples are synthetic. This is a compact portfolio project, not a claim of production deployment.

## Design choices

Small pure functions hold the core logic; the CLI handles files, JSON output and exit codes. Invalid inputs fail explicitly instead of silently changing the data.

## License

MIT. Maintained by [Kaique Dias](https://github.com/DrKaiqueDias).
