# Chapter 1 executable examples

These small, deterministic examples are teaching aids, not production recommenders or benchmark reproductions.

Run all checks from the repository root:

~~~bash
python -m unittest discover -s tests -v
~~~

| Module | Demonstration |
|---|---|
| lesson_1_1_1.py | Transparent heuristic ranking with explicit exclusions |
| lesson_1_1_2.py | Expected watch time per impression |
| lesson_1_1_3.py | A simplified e-commerce GMV funnel |
| lesson_1_2_1.py | Vector scoring and list-level category caps |
| lesson_1_2_2.py | Timestamp validation and idempotent event de-duplication |

Each example documents its assumptions in the source. No third-party package is required.
