from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .adapters import HermesRuntimeAdapter
from .capabilities import CapabilityBus
from .engine import MacesEngine
from .store import CognitiveStore


def _load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(prog="maces")
    parser.add_argument("--db", default="maces.db")
    sub = parser.add_subparsers(dest="command", required=True)

    observe = sub.add_parser("observe")
    observe.add_argument("event_json")

    inspect = sub.add_parser("inspect")
    inspect.add_argument("table")

    influence = sub.add_parser("influence")
    influence.add_argument("subject")

    sub.add_parser("capabilities")

    approve = sub.add_parser("approve-learning")
    approve.add_argument("proposal_id")

    args = parser.parse_args()
    store = CognitiveStore(args.db)
    bus = CapabilityBus()
    engine = MacesEngine(store, capabilities=bus)

    if args.command == "observe":
        event = HermesRuntimeAdapter().normalize(_load(args.event_json))
        output = engine.observe(event)
    elif args.command == "inspect":
        output = store.list_table(args.table)
    elif args.command == "influence":
        output = asdict(engine.influence(args.subject))
    elif args.command == "capabilities":
        output = bus.capabilities()
    else:
        store.set_learning_status(args.proposal_id, "approved")
        output = {"proposal_id": args.proposal_id, "status": "approved"}
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
