# 3806ICT Assignment 1 Submission Checklist

## What is included

- `src/reasoner.py` - parser, baseline Algorithm 2-style backward proof search, improved proof search, and CSV runner.
- `src/generate_benchmarks.py` - generator for the 360-formula synthetic benchmark.
- `datasets/` - textbook examples, small balanced set, quantifier stress set, and three large generated benchmark files.
- `results/` - per-formula CSV outputs and `aggregate_summary.csv`.
- `report/report_draft.tex` - LNCS-style report source.
- `report/report_draft.pdf` - compiled PDF draft.
- `appendix/AI_acknowledgement_appendix.md` - AI-use acknowledgement appendix.

## Before submitting

1. Upload the code to a GitHub repository or another accepted location.
2. Replace `TODO-INSERT-SOURCE-CODE-LINK` in `report/report_draft.tex` with the repository URL.
3. Recompile the report PDF after replacing the link.
4. Read and edit the report so the final wording is your own.
5. Keep the report within the 8-page LNCS limit, excluding the AI-use appendix if your lecturer accepts it as an appendix outside the page limit.
6. Check that the final PDF includes: abstract, introduction, proposed approach, workflow figure, datasets, implementation and experiment, results table, discussion/conclusion, data availability, and references.
7. If submitting only one PDF, append or copy the AI acknowledgement appendix after the references, as instructed in the lecture discussion.

## Re-running the experiments

From the root folder:

```bash
python3 src/generate_benchmarks.py
python3 src/reasoner.py datasets/generated_large_propositional.fol --csv results/generated_large_propositional_results.csv --max-steps 100
python3 src/reasoner.py datasets/generated_large_medium.fol --csv results/generated_large_medium_results.csv --max-steps 100
python3 src/reasoner.py datasets/generated_large_quantifier.fol --csv results/generated_large_quantifier_results.csv --max-steps 100
```

If a local Python installation has unusual site-package startup behaviour, run with:

```bash
python3 -S src/reasoner.py datasets/generated_large_quantifier.fol --csv results/generated_large_quantifier_results.csv --max-steps 100
```
