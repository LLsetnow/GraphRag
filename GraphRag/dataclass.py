from dataclasses import dataclass


@dataclass
class Document:
    """Document class definition."""

    text: str
    id: str

async def main():
    # read the docs
    with open("..//input//textbook.txt", "r", encoding="utf-8") as f:
        file = f.readlines()

    docs = []
    for id, doc in enumerate(file):
        docs.append(Document(id=id, text=doc))

    print(docs[0].text)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())