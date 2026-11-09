# Defence outline: ten minutes

Slides: `docs/defence/defence_slides.pdf`. Two speakers: Lynn-Aurea (slides 1-3, 8, 9, 11) and Sereine (slides 4-7, 10). Every figure comes from a run recorded in `runs/` (model `anthropic/claude-haiku-4.5`, 2026-11-09, `evals/test_cases.csv`).

1. **The task and the users (1 min 30, slides 1-3).** A classifier with seven labels for the support inbox; why a classifier (ADR 0001); why no retrieval: 4/4 right from the ticket alone (ADR 0003).
2. **How it works (1 min, slide 4).** Ticket in its own field, `src/llm.py` checks every answer (Pydantic, stop_reason, at most two re-prompts, one log row per call), `src/guardrails.py` builds what is sent (ADR 0002).
3. **How well, at what cost (3 min, slides 5-8).** 30 checked cases; exact match first; few-shot 27/30 at $0.74 per 1,000 calls and 1.16 s p90; Pareto front; one case = 3.3 points; the judge agrees with our hand scores on 31 of 40, and the swap changed 15 of 90 verdicts.
4. **How it fails, and how it resists misuse (2 min, slides 9-10).** L04-26 spelled out (a carburettor labelled returns_refunds: cause, the prompt); the injection case L01-10, forced to review by code; the live injection tests.
5. **The recommendation (45 s, slide 11).** Few-shot on Claude Haiku 4.5, with label definitions added and the 30 cases run again before go-live (ADR 0004).

Keep one minute spare. Rehearse once, timed, with both of us speaking. Slide 12 is a backup for questions on the four decision records.
