"""
AIVONEX – Brand Monitoring System
Sentiment Analysis Engine
Dual-model: VADER (speed) + TextBlob (subjectivity)
"""

import re
import json
from datetime import datetime
from typing import Optional
from loguru import logger

# VADER
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# TextBlob
from textblob import TextBlob

# NLTK
import nltk
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)
try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords", quiet=True)

try:
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    STOP_WORDS = set(stopwords.words("english"))
except Exception:
    STOP_WORDS = {
        "i", "me", "my", "we", "our", "you", "he", "she", "it", "they",
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
        "for", "of", "with", "is", "are", "was", "were", "be", "been",
        "have", "has", "had", "do", "did", "will", "would", "can", "could",
        "this", "that", "these", "those", "not", "no", "so", "if", "as",
    }
    def word_tokenize(text):  # noqa: F811
        return text.split()


class SentimentAnalyzer:
    """
    Dual-engine sentiment analyzer.
    Primary  : VADER  – fast, rule-based, handles social media slang / emoji
    Secondary: TextBlob – statistical, gives polarity + subjectivity
    Final label determined by weighted ensemble.
    """

    POSITIVE_THRESHOLD = 0.05
    NEGATIVE_THRESHOLD = -0.05

    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        logger.info("SentimentAnalyzer initialized (VADER + TextBlob)")

    # ── Text Cleaning ──────────────────────────────────────────────────────────

    def clean_text(self, text: str) -> str:
        text = re.sub(r"http\S+|www\S+", "", text)          # remove URLs
        text = re.sub(r"@\w+", "", text)                      # remove @mentions
        text = re.sub(r"#(\w+)", r"\1", text)                 # keep hashtag text
        text = re.sub(r"[^\w\s\!\?\.\,\'\"\-]", " ", text)   # keep punctuation
        text = re.sub(r"\s+", " ", text).strip()
        return text

    # ── Entity / Keyword Extraction ────────────────────────────────────────────

    def extract_keywords(self, text: str, top_n: int = 8) -> list[str]:
        tokens = word_tokenize(text.lower())
        keywords = [
            w for w in tokens
            if w.isalpha() and w not in STOP_WORDS and len(w) > 2
        ]
        from collections import Counter
        return [w for w, _ in Counter(keywords).most_common(top_n)]

    # ── Core Analysis ─────────────────────────────────────────────────────────

    def analyze(self, text: str, brand_keywords: Optional[list] = None) -> dict:
        """
        Returns a dict with:
          label, compound, pos, neg, neu, polarity, subjectivity,
          confidence, keywords_found, keywords, clean_text
        """
        if not text or not text.strip():
            return self._empty_result()

        clean = self.clean_text(text)

        # ── VADER ──
        vs = self.vader.polarity_scores(clean)
        compound = vs["compound"]

        # ── TextBlob ──
        blob = TextBlob(clean)
        polarity    = blob.sentiment.polarity        # -1 → +1
        subjectivity= blob.sentiment.subjectivity    # 0 → 1

        # ── Ensemble label ──
        # Weight VADER 60%, TextBlob 40%
        ensemble_score = 0.6 * compound + 0.4 * polarity
        label = self._score_to_label(ensemble_score)

        # ── Confidence ──
        confidence = min(abs(ensemble_score) * 1.6, 1.0)
        if subjectivity < 0.2:
            confidence *= 0.85   # factual text → lower confidence

        # ── Keywords found in text ──
        keywords_found = []
        if brand_keywords:
            text_lower = text.lower()
            keywords_found = [kw for kw in brand_keywords if kw.lower() in text_lower]

        extracted_keywords = self.extract_keywords(clean)

        return {
            "sentiment_label":        label,
            "vader_compound":         round(compound, 4),
            "vader_pos":              round(vs["pos"], 4),
            "vader_neg":              round(vs["neg"], 4),
            "vader_neu":              round(vs["neu"], 4),
            "textblob_polarity":      round(polarity, 4),
            "textblob_subjectivity":  round(subjectivity, 4),
            "confidence":             round(confidence, 4),
            "ensemble_score":         round(ensemble_score, 4),
            "keywords_found":         keywords_found,
            "keywords":               extracted_keywords,
            "clean_text":             clean,
            "char_count":             len(text),
            "word_count":             len(text.split()),
        }

    def analyze_batch(self, texts: list[str], brand_keywords: Optional[list] = None) -> list[dict]:
        results = []
        for text in texts:
            try:
                results.append(self.analyze(text, brand_keywords))
            except Exception as e:
                logger.warning(f"Analysis failed for text: {e}")
                results.append(self._empty_result())
        return results

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _score_to_label(self, score: float) -> str:
        if score >= self.POSITIVE_THRESHOLD:
            return "positive"
        elif score <= self.NEGATIVE_THRESHOLD:
            return "negative"
        return "neutral"

    def _empty_result(self) -> dict:
        return {
            "sentiment_label": "neutral",
            "vader_compound": 0.0, "vader_pos": 0.0,
            "vader_neg": 0.0, "vader_neu": 1.0,
            "textblob_polarity": 0.0, "textblob_subjectivity": 0.0,
            "confidence": 0.0, "ensemble_score": 0.0,
            "keywords_found": [], "keywords": [],
            "clean_text": "", "char_count": 0, "word_count": 0,
        }

    # ── Summary Stats ─────────────────────────────────────────────────────────

    def compute_summary(self, results: list[dict]) -> dict:
        if not results:
            return {}

        total = len(results)
        pos   = sum(1 for r in results if r["sentiment_label"] == "positive")
        neg   = sum(1 for r in results if r["sentiment_label"] == "negative")
        neu   = total - pos - neg

        avg_compound = sum(r["vader_compound"] for r in results) / total
        avg_subjectivity = sum(r["textblob_subjectivity"] for r in results) / total

        # Brand Health Score: 0–100
        health = round(((avg_compound + 1) / 2) * 100, 1)

        return {
            "total_mentions":      total,
            "positive_count":      pos,
            "negative_count":      neg,
            "neutral_count":       neu,
            "positive_pct":        round(pos / total * 100, 1),
            "negative_pct":        round(neg / total * 100, 1),
            "neutral_pct":         round(neu / total * 100, 1),
            "avg_compound":        round(avg_compound, 4),
            "avg_subjectivity":    round(avg_subjectivity, 4),
            "brand_health_score":  health,
        }


# ── Singleton ─────────────────────────────────────────────────────────────────
_analyzer: Optional[SentimentAnalyzer] = None


def get_analyzer() -> SentimentAnalyzer:
    global _analyzer
    if _analyzer is None:
        _analyzer = SentimentAnalyzer()
    return _analyzer
