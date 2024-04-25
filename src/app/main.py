import argparse
from pathlib import Path
from typing import Union, Dict

import docx
from elasticsearch import Elasticsearch
from jboc import composed


class SearchEngine:
    def __init__(self, path):
        docs = collect_docs(path)
        client = Elasticsearch("http://localhost:9200/")

        mappings = {
            "properties": {
                "title": {"type": "text"},
                "text": {"type": "text"}
            },
        }

        client.indices.create(index="TravelLine", mappings=mappings)

        create_base(client, docs)
        self.client = client

    def __call__(self, query: str):
        return find_title(query, self.client)


def main(path: Union[str, Path]):
    docs = collect_docs(path)

    if not docs:
        print("Empty knowledge base")
        return

    client = Elasticsearch("http://localhost:9200/", api_key=None)
    create_base(client, docs)

    repl(client)


def create_base(client, docs):
    for i, (k, v) in enumerate(docs.items()):
        client.index(
            index="TravelLine",
            id=str(i),
            document=v,
        )


def repl(client):
    while True:
        query = input("Enter your question please: ")
        if not query:
            print("You haven't entered anything.")
            continue

        find_title(query, client)
        # print(f"The answer is:\n{text}")


@composed(dict)
def collect_docs(path: Union[str, Path]) -> Dict[str, Dict]:
    for p in Path(path).resolve().iterdir():
        if not p.suffix.endswith("docx"):
            continue

        text = "\n".join(read_docx(p))
        title = p.stem
        yield p.stem, {"title": title, "text": text}


def find_title(query: str, client):
    resp = client.search(query={"match": {"title": {"query": query}, "text": {"query": query}}})
    print("Got {} hits:".format(resp["hits"]["total"]["value"]))
    for hit in resp["hits"]["hits"]:
        print("{title}\n{text}".format(**hit["_source"]))


def read_docx(path):
    return [p.text for p in docx.Document(path).paragraphs]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-path", "-bp", help="Knowledge base path.")

    args = parser.parse_args()
    main(args.base_path)