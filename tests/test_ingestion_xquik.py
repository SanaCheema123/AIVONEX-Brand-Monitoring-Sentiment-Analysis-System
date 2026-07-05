import unittest
import sys
import types

if "loguru" not in sys.modules:
    logger = types.SimpleNamespace(info=lambda *args, **kwargs: None)
    sys.modules["loguru"] = types.SimpleNamespace(logger=logger)

from app.services.ingestion import DataIngestionService


class DataIngestionXquikTest(unittest.TestCase):
    def test_parse_csv_bytes_detects_xquik_aliases(self):
        content = (
            "tweet_id,created_at,full_text,username,like_count,retweet_count,reply_count\n"
            "100,2026-07-05T12:00:00,Great launch,user_a,10,4,2\n"
        ).encode("utf-8")

        records = DataIngestionService().parse_csv_bytes(content)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["text"], "Great launch")
        self.assertEqual(records[0]["source"], "X")
        self.assertEqual(records[0]["author"], "user_a")
        self.assertEqual(records[0]["mention_date"], "2026-07-05T12:00:00")
        self.assertEqual(records[0]["engagement"], 16)

    def test_explicit_mapping_is_case_insensitive(self):
        content = (
            "Message,Network,Handle,Published At,Score\n"
            "Needs follow up,Forum,analyst,2026-07-05,7\n"
        ).encode("utf-8")

        records = DataIngestionService().parse_csv_bytes(
            content,
            text_column="Message",
            source_column="Network",
            author_column="Handle",
            date_column="Published At",
            engagement_column="Score",
        )

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["text"], "Needs follow up")
        self.assertEqual(records[0]["source"], "Forum")
        self.assertEqual(records[0]["author"], "analyst")
        self.assertEqual(records[0]["mention_date"], "2026-07-05T00:00:00")
        self.assertEqual(records[0]["engagement"], 7)


if __name__ == "__main__":
    unittest.main()
