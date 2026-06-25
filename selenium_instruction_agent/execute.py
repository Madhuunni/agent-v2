"""Execution phase: read a prompt, classify broad intent, print JSON only."""

import argparse
import json
import sys

import torch

from config import CONFIDENCE_THRESHOLD, DATA_FILE
from instruction_builder import build_instruction
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize


def predict_intent(prompt: str, debug: bool = False) -> str:
    data = torch.load(DATA_FILE, map_location=torch.device("cpu"), weights_only=False)
    model = NeuralNet(data["input_size"], data["hidden_size"], data["output_size"])
    model.load_state_dict(data["model_state"])
    model.eval()

    vector = bag_of_words(tokenize(prompt), data["all_words"])
    output = model(torch.from_numpy(vector).reshape(1, vector.shape[0]))
    probabilities = torch.softmax(output, dim=1)
    confidence, predicted = torch.max(probabilities, dim=1)
    tag = data["tags"][predicted.item()]
    if debug:
        print(f"DEBUG predicted_intent={tag} confidence={confidence.item():.3f}", file=sys.stderr)
    return tag if confidence.item() >= CONFIDENCE_THRESHOLD else "unknown"


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert a browser automation prompt to JSON instructions.")
    parser.add_argument("--debug", action="store_true", help="Print model diagnostics to stderr.")
    args = parser.parse_args()

    prompt = input("User prompt: ")
    predicted_intent = predict_intent(prompt, debug=args.debug)
    plan = build_instruction(prompt, predicted_intent)
    print(json.dumps(plan.model_dump(), indent=2))


if __name__ == "__main__":
    main()
