import argparse
from pathlib import Path
from typing import Union, Iterable, Optional, Dict, Tuple

from Levenshtein import distance
from deli import load_text
from jboc import composed, collect
import docx


class SearchEngine:
    def __init__(self, path: str):
        self.titles = collect_titles(path)

    def __call__(self, query: str):
        return find_title(query, self.titles)


def main(path: Union[str, Path]):
    titles = collect_titles(path)
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

        text = find_title(query, titles)
        print(f"The answer is:\n{text}")


@composed(dict)
def collect_titles(path: Union[str, Path]) -> Dict[str, str]:
    for p in Path(path).resolve().iterdir():
        if not p.suffix.endswith("docx"):
            continue

        yield p.stem, "\n".join(read_docx(p))


def find_title(query: str, titles: Dict[str, str]) -> Optional[str]:
    _, text = min(titles.items(), key=lambda t: distance(query.lower(), t[0].lower()))
    return text


def read_docx(path):
    return [p.text for p in docx.Document(path).paragraphs]


if __name__  == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-path", "-bp", help="Knowledge base path.")

    args = parser.parse_args()
    main(args.base_path)
