from __future__ import annotations

import argparse
import json
from pathlib import Path

from .adapters import HermesRuntimeAdapter
from .engine import MacesEngine
from .models import ActivationLevel
from .policy import MacesPolicy
from .store import CognitiveStore


def _load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(prog="maces")
    parser.add_argument("--db", default="maces.db")
    parser.add_argument("--activation", choices=[v.value for v in ActivationLevel], default="shadow")
    sub = parser.add_subparsers(dest="command", required=True)

    observe = sub.add_parser("observe")
    observe.add_argument("event_json")

    inspect = sub.add_parser("inspect")
    inspect.add_argument("table")

    approve = sub.add_parser("approve-learning")
    approve.add_argument("proposal_id")

    args = parser.parse_args()
    store = CognitiveStore(args.db)
    policy = MacesPolicy(activation=ActivationLevel(args.activation))
    engine = MacesEngine(store, policy)

    if args.command == "observe":
        event = HermesRuntimeAdapter().normalize(_load(args.event_json))
        print(json.dumps(engine.observe(event), ensure_ascii=False, indent=2))
    elif args.command == "inspect":
        print(json.dumps(store.list_table(args.table), ensure_ascii=False, indent=2))
    elif args.command == "approve-learning":
        store.set_learning_status(args.proposal_id, "approved")
        print(json.dumps({"proposal_id": args.proposal_id, "status": "approved"}))


if __name__ == "__main__":
    main()
