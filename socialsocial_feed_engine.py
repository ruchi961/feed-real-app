import json
from pathlib import Path

from social_feed_engine import SocialFeedEngine


DATA_FILE = Path(__file__).with_name("social_feed_dummy_data.json")


def main() -> None:
    with DATA_FILE.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    engine = SocialFeedEngine(payload)

    print("Feed for user 1:")
    for item in engine.get_feed(1, limit=5):
        print(item)

    print("\nSearch results for query 'funny travel stories from last week':")
    for item in engine.search(1, "funny travel stories from last week", limit=5):
        print(item)


if __name__ == "__main__":
    main()
