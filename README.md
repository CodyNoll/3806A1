# 3806ICT Assignment 1 – Automated Reasoning

This repository contains the source code, benchmark datasets, and experiment results for my 3806ICT Logic and Automated Reasoning Assignment 1.

The project implements and evaluates a small automated reasoner for first-order logic. The baseline method follows the naive backward proof-search strategy described as Algorithm 2 in Hou's *Fundamentals of Logic and Computation*. The improved method keeps the same LK′ sequent-calculus rules but adds practical search-control mechanisms to reduce repeated work and improve behaviour on some quantifier-heavy cases.

## Repository Contents

```text
3806A1/
├── src/
│   ├── reasoner.py
│   └── generate_benchmarks.py
├── datasets/
│   ├── generated_balanced.fol
│   ├── generated_large_medium.fol
│   ├── generated_large_propositional.fol
│   ├── generated_large_quantifier.fol
│   ├── quantifier_stress.fol
│   └── textbook_examples.fol
├── results/
│   ├── aggregate_summary.csv
│   ├── generated_balanced_results.csv
│   ├── generated_large_medium_results.csv
│   ├── generated_large_propositional_results.csv
│   ├── generated_large_quantifier_results.csv
│   ├── quantifier_stress_results.csv
│   └── textbook_examples_results.csv
```

## Source Code

### `src/reasoner.py`

This is the main implementation file. It includes:

- lexer and parser for first-order logic formulae;
- abstract syntax tree classes;
- substitution and free-term handling;
- sequent representation;
- baseline backward proof search;
- improved proof search;
- CSV experiment output.

### `src/generate_benchmarks.py`

This script generates additional benchmark formula files used to test the reasoner on a larger set of cases.

## Benchmark Datasets

The `datasets/` folder contains six benchmark files:

- `textbook_examples.fol` – small examples based on textbook and lecture-style formulae.
- `quantifier_stress.fol` – hand-designed examples that stress quantifier handling.
- `generated_balanced.fol` – small balanced benchmark for readable debugging.
- `generated_large_propositional.fol` – larger propositional benchmark.
- `generated_large_medium.fol` – medium-difficulty propositional benchmark.
- `generated_large_quantifier.fol` – larger first-order benchmark focused on quantifier interaction.

The generated benchmark files include a mixture of valid and invalid formulae. They were used to compare the baseline and improved search strategies across easy, medium, and quantifier-focused cases.

## Experiment Results

The `results/` folder contains CSV files produced by running the reasoner over the benchmark datasets.

The most important file is:

```text
results/aggregate_summary.csv
```

This summarises the baseline and improved methods across each dataset, including:

- number of formulae tested;
- number proved valid;
- number not proved;
- number reaching step/depth limits;
- average search steps;
- average generated fresh terms.

## How to Run

This project uses Python 3 and the standard library only. No external automated theorem prover, SAT solver, or SMT solver is required.

From the repository root, run a dataset like this:

```bash
py src/reasoner.py datasets/generated_balanced.fol
```

or, depending on your Python installation:

```bash
python src/reasoner.py datasets/generated_balanced.fol
```

To save results to a CSV file:

```bash
py src/reasoner.py datasets/generated_balanced.fol --csv results/test_generated_balanced_results.csv
```

To regenerate benchmark datasets:

```bash
py src/generate_benchmarks.py
```

## Example

Running:

```bash
py src/reasoner.py datasets/generated_balanced.fol
```

prints baseline and improved proof-search results for each formula in the dataset.

A formula is reported as valid only when all proof-search branches close. If a branch remains open or a step/depth limit is reached, the program reports that the formula was not proved rather than claiming it is invalid.

## Notes on the Improved Method

The improved method is not a wrapper around an existing solver. It uses the same proof-calculus rules as the baseline but changes the management of proof search by adding:

- caching of explored sequents;
- deterministic rule ordering;
- bounded term generation;
- limited backtracking over alternative applicable rules.

These changes are intended to reduce redundant computation and improve proof search on some quantifier-heavy formulae.

## Data Availability

This repository is linked in the Data Availability section of the submitted report and contains the source code, generated datasets, and experiment result files used for the assignment.
