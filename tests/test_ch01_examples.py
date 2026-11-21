"""Unit tests for the five chapter-one teaching examples."""

import unittest

from examples.ch01.lesson_1_1_1 import rank_candidates, score_candidate
from examples.ch01.lesson_1_1_2 import expected_watch_time, rank_impressions
from examples.ch01.lesson_1_1_3 import estimate_gmv, apply_relative_lift
from examples.ch01.lesson_1_2_1 import dot, rank_items
from examples.ch01.lesson_1_2_2 import deduplicate_events, normalize_event


class RecommendationExampleTests(unittest.TestCase):
    def test_toy_ranker_filters_blocked_items(self):
        items = [
            {"id": "a", "tags": {"science"}, "quality": 0.9, "freshness": 0.8},
            {"id": "b", "tags": {"fashion"}, "quality": 1.0, "freshness": 1.0},
            {"id": "c", "tags": {"history", "science"}, "quality": 0.8, "freshness": 0.3},
        ]
        self.assertEqual(rank_candidates({"science", "history"}, items, {"b"}), ["c", "a"])
        with self.assertRaises(ValueError):
            score_candidate({"science"}, {"science"}, 1.2)

    def test_expected_watch_time_not_ctr_alone(self):
        self.assertEqual(expected_watch_time(0.2, 180), 36)
        rows = [
            {"video_id": "clickbait", "click_probability": 0.8, "conditional_watch_seconds": 10},
            {"video_id": "useful", "click_probability": 0.2, "conditional_watch_seconds": 180},
        ]
        self.assertEqual(rank_impressions(rows), ["useful", "clickbait"])
        with self.assertRaises(ValueError):
            expected_watch_time(1.2, 10)

    def test_gmv_funnel_and_relative_lift(self):
        self.assertAlmostEqual(estimate_gmv(1_000_000, 0.12, 0.04, 260), 1_248_000)
        self.assertAlmostEqual(apply_relative_lift(100, 0.01), 101)
        with self.assertRaises(ValueError):
            estimate_gmv(10, 1.1, 0.2, 20)

    def test_retrieval_score_and_list_constraint(self):
        self.assertAlmostEqual(dot([1, 2], [3, 4]), 11)
        items = [
            {"id": "video-a", "category": "video", "vector": [0.9, 0.0, 0.6]},
            {"id": "video-b", "category": "video", "vector": [0.8, 0.1, 0.6]},
            {"id": "article-c", "category": "article", "vector": [0.7, 0.2, 0.8]},
        ]
        self.assertEqual(rank_items([0.8, 0.1, 0.7], items, max_per_category=1), ["video-a", "article-c"])
        with self.assertRaises(ValueError):
            dot([1], [1, 2])

    def test_event_validation_and_deduplication(self):
        first = {"event_id":"e1","user_id":"u1","item_id":"i1","event_type":"click","event_time":"2026-11-20T10:00:00+08:00"}
        duplicate = {"event_id":"e1","user_id":"u1","item_id":"i1","event_type":"click","event_time":"2026-11-20T02:00:00Z"}
        unique = deduplicate_events([first, duplicate])
        self.assertEqual(len(unique), 1)
        self.assertTrue(unique[0]["event_time"].endswith("+00:00"))
        naive = dict(first, event_time="2026-11-20T10:00:00")
        with self.assertRaises(ValueError):
            normalize_event(naive)


if __name__ == "__main__":
    unittest.main()
