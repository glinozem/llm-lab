from __future__ import annotations

import argparse

from llm_lab.factory import LLMFactory
from llm_lab.types import Message


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--provider", default="ollama", choices=["ollama"])
    p.add_argument("--prompt", required=True)
    args = p.parse_args()

    client = LLMFactory.create(args.provider)
    messages: list[Message] = [{"role": "user", "content": args.prompt}]
    print(client.generate(messages))


if __name__ == "__main__":
    main()
