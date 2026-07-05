"""
AIVONEX – Brand Monitoring System
Data Ingestion Service
Supports: CSV upload, manual text, simulated social feed
"""

import random
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional
from loguru import logger


# ─── Simulated Social Media Posts ─────────────────────────────────────────────
TEMPLATES = {
    "positive": [
        "{brand} just released an amazing update! Totally impressed 🔥",
        "Been using {brand} for months – absolutely love it. Highly recommend!",
        "{brand}'s customer support resolved my issue within minutes. Outstanding!",
        "Just tried {brand} for the first time. 10/10 would recommend 🙌",
        "{brand} is hands down the best in the market right now 💯",
        "Shoutout to {brand} for always delivering quality. Never disappointed.",
        "Why did I wait so long to try {brand}? Game changer!",
        "{brand} keeps getting better with every release. Kudos to the team!",
        "Incredibly smooth experience with {brand} today. Impressed!",
        "Just recommended {brand} to all my colleagues. Top tier product.",
    ],
    "negative": [
        "{brand} customer service is the worst I've ever experienced 😤",
        "Disappointed with {brand}'s latest update. Many bugs, very slow.",
        "Still waiting for {brand} to fix this critical issue. Very frustrating.",
        "{brand} raised prices again but the quality is worse. Not worth it.",
        "Switched away from {brand} after years. Poor support, buggy product.",
        "Warning: {brand} billing system charged me twice. Avoid!",
        "{brand} has serious data privacy concerns nobody is talking about.",
        "The new {brand} update broke everything. What happened to QA?",
        "Completely let down by {brand} today. Expected much better.",
        "{brand} is really going downhill lately. Used to be great.",
    ],
    "neutral": [
        "Anyone know if {brand} supports API integration with Slack?",
        "Comparing {brand} vs competitors this week for our company decision.",
        "{brand} announced a new partnership. Will have to see how it goes.",
        "Does {brand} offer a free trial? Looking to test before buying.",
        "Read an interesting article about {brand}'s roadmap for Q4.",
        "{brand} just opened a new office in Dubai apparently.",
        "Curious about {brand}'s pricing changes this quarter.",
        "Has anyone migrated from {brand} recently? Thoughts?",
        "Looking at {brand} for our next project. Any experience?",
        "{brand} is trending on LinkedIn today.",
    ],
}

SOURCES = ["Twitter", "Reddit", "LinkedIn", "News", "Review Site", "Forum"]
AUTHORS = [
    "tech_guru42", "sarah_j", "priya_dev", "marketer_mike",
    "startup_founder", "digital_nomad", "b2b_pro", "analyst_rasha",
    "cto_thoughts", "ux_designer_p", "product_hunter", "enterprise_lead",
]

CSV_COLUMN_ALIASES = {
    "text": [
        "text", "full_text", "tweet_text", "content", "post",
        "review", "comment", "message", "body",
    ],
    "date": ["mention_date", "created_at", "timestamp", "published_at", "date"],
    "source": ["source", "platform", "network"],
    "author": ["author", "username", "user", "screen_name", "handle"],
    "engagement": [
        "engagement", "likes", "like_count", "retweets", "retweet_count",
        "replies", "reply_count", "quotes", "quote_count", "upvotes",
    ],
}

XQUIK_EXPORT_MARKERS = {
    "tweet_id", "full_text", "tweet_text", "retweet_count",
    "like_count", "screen_name",
}


class DataIngestionService:

    # ── CSV Import ─────────────────────────────────────────────────────────────

    def parse_csv(self, file_path: str, text_column: str = "text",
                  date_column: Optional[str] = None,
                  source_column: Optional[str] = None,
                  author_column: Optional[str] = None,
                  engagement_column: Optional[str] = None) -> list[dict]:
        """
        Parse a CSV file and return list of mention dicts.
        Required column: text_column (defaults to 'text')
        """
        df = pd.read_csv(file_path)
        records = self._records_from_dataframe(
            df,
            text_column=text_column,
            date_column=date_column,
            source_column=source_column,
            author_column=author_column,
            engagement_column=engagement_column,
        )
        logger.info(f"CSV parsed: {len(records)} valid records from '{file_path}'")
        return records

    def parse_csv_bytes(self, content: bytes, **kwargs) -> list[dict]:
        import io
        df = pd.read_csv(io.BytesIO(content))
        return self._records_from_dataframe(df, **kwargs)

    def _records_from_dataframe(self, df: pd.DataFrame, text_column: str = "text",
                                date_column: Optional[str] = None,
                                source_column: Optional[str] = None,
                                author_column: Optional[str] = None,
                                engagement_column: Optional[str] = None) -> list[dict]:
        df.columns = [c.strip().lower() for c in df.columns]
        columns = list(df.columns)

        text_col = self._select_column(columns, text_column, CSV_COLUMN_ALIASES["text"]) or columns[0]
        date_col = self._select_column(columns, date_column, CSV_COLUMN_ALIASES["date"])
        source_col = self._select_column(columns, source_column, CSV_COLUMN_ALIASES["source"])
        author_col = self._select_column(columns, author_column, CSV_COLUMN_ALIASES["author"])
        engagement_col = self._select_column(columns, engagement_column, []) if engagement_column else None
        default_source = "X" if XQUIK_EXPORT_MARKERS.intersection(columns) else "CSV"

        records = []
        for _, row in df.iterrows():
            text = str(row.get(text_col, "")).strip()
            if not text or text.lower() == "nan":
                continue

            source = default_source
            if source_col:
                source = self._clean_cell(row.get(source_col, default_source), default_source)

            author = "unknown"
            if author_col:
                author = self._clean_cell(row.get(author_col, "unknown"), "unknown")

            mention_date = datetime.utcnow().isoformat()
            if date_col:
                mention_date = self._parse_date(str(row.get(date_col, "")))

            record = {
                "text":   text,
                "source": source,
                "author": author,
                "mention_date": mention_date,
                "engagement": self._row_engagement(row, engagement_col),
            }
            records.append(record)

        return records

    # ── Simulated Social Feed ─────────────────────────────────────────────────

    def generate_simulated_mentions(
        self, brand_name: str, n: int = 50,
        pos_pct: float = 0.45, neg_pct: float = 0.25,
        days_back: int = 30
    ) -> list[dict]:
        """
        Generate realistic simulated mentions for demo / testing.
        Sentiment distribution matches given percentages.
        """
        records = []
        pos_n = int(n * pos_pct)
        neg_n = int(n * neg_pct)
        neu_n = n - pos_n - neg_n

        label_counts = (
            [("positive", pos_n)] + [("negative", neg_n)] + [("neutral", neu_n)]
        )

        for label, count in label_counts:
            templates = TEMPLATES[label]
            for _ in range(count):
                text = random.choice(templates).format(brand=brand_name)
                dt = datetime.utcnow() - timedelta(
                    days=random.randint(0, days_back),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59),
                )
                records.append({
                    "text":         text,
                    "source":       random.choice(SOURCES),
                    "author":       random.choice(AUTHORS),
                    "mention_date": dt.isoformat(),
                    "engagement":   random.randint(0, 2000),
                    "reach":        random.randint(100, 50000),
                    "_hint_label":  label,   # for testing only
                })

        random.shuffle(records)
        logger.info(f"Generated {len(records)} simulated mentions for '{brand_name}'")
        return records

    # ── Manual Text ───────────────────────────────────────────────────────────

    def prepare_manual(self, text: str, source: str = "manual") -> dict:
        return {
            "text":         text,
            "source":       source,
            "author":       "manual_input",
            "mention_date": datetime.utcnow().isoformat(),
            "engagement":   0,
            "reach":        0,
        }

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _normalize_column(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        return value.strip().lower()

    def _select_column(self, columns: list[str], preferred: Optional[str], aliases: list[str]) -> Optional[str]:
        preferred_column = self._normalize_column(preferred)
        if preferred_column and preferred_column in columns:
            return preferred_column
        for alias in aliases:
            if alias in columns:
                return alias
        return None

    def _clean_cell(self, value, fallback: str) -> str:
        text = str(value).strip()
        if not text or text.lower() == "nan":
            return fallback
        return text

    def _parse_int(self, value) -> int:
        try:
            return int(float(str(value).replace(",", "").strip()))
        except (TypeError, ValueError):
            return 0

    def _row_engagement(self, row, engagement_column: Optional[str]) -> int:
        if engagement_column:
            return self._parse_int(row.get(engagement_column, 0))

        direct_engagement = self._parse_int(row.get("engagement", 0))
        if direct_engagement:
            return direct_engagement

        return sum(
            self._parse_int(row.get(column, 0))
            for column in CSV_COLUMN_ALIASES["engagement"]
            if column != "engagement"
        )

    def _parse_date(self, date_str: str) -> str:
        for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S"]:
            try:
                return datetime.strptime(date_str, fmt).isoformat()
            except (ValueError, TypeError):
                continue
        return datetime.utcnow().isoformat()


# ── Singleton ─────────────────────────────────────────────────────────────────
_ingestion: Optional[DataIngestionService] = None


def get_ingestion_service() -> DataIngestionService:
    global _ingestion
    if _ingestion is None:
        _ingestion = DataIngestionService()
    return _ingestion
