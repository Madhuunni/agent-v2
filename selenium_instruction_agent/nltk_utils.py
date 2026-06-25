"""Tokenization, stemming, and bag-of-words helpers."""

import re
from typing import Iterable, List

import numpy as np
from nltk.stem.porter import PorterStemmer

stemmer = PorterStemmer()


def tokenize(sentence: str) -> List[str]:
    """Split text into word-like tokens without requiring downloaded NLTK data."""
    return re.findall(r"https?://[^\s]+|[A-Za-z0-9_#.'/-]+", sentence)


def stem(word: str) -> str:
    """Return a lowercase stemmed token."""
    return stemmer.stem(word.lower())


def bag_of_words(tokenized_sentence: Iterable[str], words: List[str]) -> np.ndarray:
    """Create a binary bag-of-words vector for the known vocabulary."""
    sentence_words = {stem(word) for word in tokenized_sentence}
    bag = np.zeros(len(words), dtype=np.float32)
    for idx, word in enumerate(words):
        if word in sentence_words:
            bag[idx] = 1.0
    return bag
