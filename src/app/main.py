import argparse
from pathlib import Path
from typing import Union, Iterable, Optional, Dict, Tuple

from Levenshtein import distance
from deli import load_text
from jboc import composed, collect
import docx
import re
import string

import pymorphy2


class Morpholyzer:
    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()

    def __call__(self, word: str) -> str:
        return self.morph.parse(word)[0].normal_form

    def normalize_sentence(self, sentence: str) -> str:
        regex = re.compile('[%s]' % re.escape(string.punctuation))
        return " ".join([self(w) for w in regex.sub('', sentence).lower().split(" ")])


class SearchEngine:
    def __init__(self, path: str):
        self.morph = Morpholyzer()
        self.titles = {title: {
            "content": content,
            "normalized_title": " ".join(self.morph.normalize_sentence(title))
        } for title, content in collect_titles(path).items()}

    def __call__(self, query: str, data: Optional[dict] = None):
        normalized_query = self.morph.normalize_sentence(query)
        data = {t: {
                    "content": c,
                    "normalized_title": " ".join(self.morph.normalize_sentence(t))
                } for t, c in data.items()} if data else self.titles
        return find_title(normalized_query, data)


def main(path: Union[str, Path]):
    titles = SearchEngine(path).titles
    repl(titles)


def repl(titles: Dict[str, str]):
    if not titles:
        print("Knowledge base is empty.")
        return

    while True:
        query = input("Enter your question please: ")
        if not query:
            print("You haven't entered anything.")
            continue

        title, text = find_title(query, titles)
        print(f"The answer is:\n{text}")


@composed(dict)
def collect_titles(path: Union[str, Path]) -> Dict[str, str]:
    for p in Path(path).resolve().iterdir():
        if not p.suffix.endswith("docx"):
            continue

        yield p.stem, "\n".join(read_docx(p))


def find_title(query: str, titles: Dict[str, str]) -> Optional[str]:
    title, text = min(titles.items(), key=lambda t: distance(query.lower(),
                                         t[1]["normalized_title"].lower())
                  )
    return title, text["content"]


def read_docx(path):
    return [p.text for p in docx.Document(path).paragraphs]


if __name__  == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-path", "-bp", help="Knowledge base path.")

    args = parser.parse_args()
    main(args.base_path)
