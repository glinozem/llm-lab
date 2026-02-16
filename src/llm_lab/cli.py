from __future__ import annotations

import argparse

from llm_lab.config import Settings
from llm_lab.factory import LLMFactory
from llm_lab.types import Message, Provider


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--provider", choices=["ollama", "openai"])
    p.add_argument("--model")
    p.add_argument("--ollama-host")
    p.add_argument("--openai-base-url")
    p.add_argument("--openai-api-key")
    p.add_argument("--system", default="You are a helpful assistant.")
    p.add_argument("--prompt", required=True)
    args = p.parse_args()

    s = Settings()
    provider: Provider = args.provider or s.llm_provider

    if args.model:
        if provider == "ollama":
            s.ollama_model = args.model
        else:
            s.openai_model = args.model

    if args.ollama_host:
        s.ollama_host = args.ollama_host
    if args.openai_base_url:
        s.openai_base_url = args.openai_base_url
    if args.openai_api_key:
        s.openai_api_key = args.openai_api_key

    client = LLMFactory.create(provider, settings=s)

    messages: list[Message] = [
        {"role": "system", "content": args.system},
        {"role": "user", "content": args.prompt},
    ]
    print(client.generate(messages))


if __name__ == "__main__":
    main()
