# Selenium Instruction Agent

A beginner-friendly local PyTorch NLP project that converts small browser automation prompts into validated JSON instruction plans. The JSON is intended for a later Selenium-script generator, but this project **does not generate Selenium code** and **does not open a browser**.

## Purpose

Example prompt:

```text
Navigate to http://localhost:4200/. Enter email and password. Click login.
```

Example output:

```json
{
  "test_name": "Login Test",
  "base_url": "http://localhost:4200/",
  "steps": [
    {
      "step_no": 1,
      "action": "navigate",
      "element": null,
      "by": null,
      "selector": null,
      "value": "http://localhost:4200/",
      "value_from_env": null,
      "description": "Navigate to the application URL"
    },
    {
      "step_no": 2,
      "action": "type",
      "element": "email",
      "by": "css selector",
      "selector": "input[type='email'], input[name='email'], input#email",
      "value": null,
      "value_from_env": "APP_EMAIL",
      "description": "Enter email from environment variable APP_EMAIL"
    },
    {
      "step_no": 3,
      "action": "type",
      "element": "password",
      "by": "css selector",
      "selector": "input[type='password'], input[name='password'], input#password",
      "value": null,
      "value_from_env": "APP_PASSWORD",
      "description": "Enter password from environment variable APP_PASSWORD"
    },
    {
      "step_no": 4,
      "action": "click",
      "element": "login button",
      "by": "css selector",
      "selector": "button[type='submit'], button.login, #login",
      "value": null,
      "value_from_env": null,
      "description": "Click the login button"
    }
  ]
}
```

## Setup

```bash
pip install -r requirements.txt
```

## Phase 1: Training

Training data lives in `intent.json`. It contains prompt patterns for navigation, email/password login, username/password login, clicks, visible-element checks, full flows, and unknown requests.

Run:

```bash
python train.py
```

This trains a small feed-forward PyTorch classifier and writes `data.pth` with the model state, vocabulary, tags, and intent metadata.

## Phase 2: Execution

Run:

```bash
python execute.py
```

Then enter a prompt. The command prints JSON only after the `User prompt:` input line. Use `--debug` only when you want model diagnostics on stderr.

## Tests

```bash
pytest
```

The tests validate URL extraction, email/password plans, username/password plans, ordered step numbers, and JSON parsing.

## How this differs from patrickloeber/pytorch-chatbot

The reference repository is a conversational intent-classification chatbot with tokenization, stemming, bag-of-words preprocessing, a simple PyTorch feed-forward model, and a chat loop that selects human-readable responses from intents. This project keeps the approachable local-training pattern, but changes the product behavior completely:

- It is not conversational.
- It classifies broad browser-automation intents.
- It uses deterministic rules to extract URLs and required fields.
- It outputs a validated JSON instruction schema.
- It never chooses random chatbot responses.
- It never generates Selenium Python code.

## Limitations

- Designed for a narrow prompt domain.
- Selectors are generic defaults and may need project-specific customization.
- The model is intentionally small and rule-assisted, not a general language model.
- Ambiguous prompts may produce fallback instructions.

## Future improvements

- Add more intent examples for richer flows.
- Add custom selector dictionaries per application.
- Support explicit field values where safe.
- Add a separate downstream Selenium-code generator.
- Add confidence reporting in a machine-readable debug file.
