# DataBuddy — Beginner Data Analysis Agent

DataBuddy is a small, explainable CSV analysis agent built with Python, Pandas, and Streamlit. It accepts a tabular CSV file and a natural-language question, selects an analysis tool, and returns a result calculated from the uploaded data.

## Features / distinct tools

1. `dataset_summary`: row count, column count, column names, and data types.
2. `missing_values`: counts missing values in each column.
3. `top_rows`: finds rows with the highest or lowest values in a numeric column.
4. `filter_rows`: filters a numeric column using `>`, `<`, `>=`, `<=`, or `=`.
5. `group_statistics`: calculates average, sum, minimum, maximum, or count by a category.
6. `correlation_matrix`: calculates correlations between numeric columns.

## Important limitation

This starter version uses transparent rule-based question matching rather than an LLM. It is intentionally simple and avoids inventing data-derived answers. It supports common question patterns; unusual phrasing may not be understood. This is a baseline to test and improve, not a claim that every natural-language question is supported.

## Run locally

1. Install Python 3.10 or newer.
2. Download or clone this repository.
3. Open a terminal in the project folder.
4. Create a virtual environment (recommended):
   - Windows: `py -m venv .venv`
   - Windows PowerShell: `.venv\\Scripts\\Activate.ps1`
   - macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`
5. Install dependencies: `pip install -r requirements.txt`
6. Run: `streamlit run app.py`
7. Open the local URL printed in the terminal. Upload a CSV or try the included demo dataset.

## Example questions

- `Give me a summary of the dataset`
- `Show missing values`
- `Show the top rows`
- `Show rows where maths > 80`
- `Average maths by section`
- `Show correlation matrix`

For grouping, use a numeric column and a category column, e.g. `average maths by section`. The current version automatically chooses the first suitable numeric column; this is a known limitation to improve.

## Run tests

```bash
pytest -q
```

## Design

The app separates analysis operations into functions. `answer_question` routes a question to one of these tools. Streamlit provides the browser interface; Pandas performs the data analysis.

## What I built / next improvements

Before submitting, write this section in your own words after testing the code. Record:
- what you changed,
- which tests you ran and their results,
- questions the agent could and could not understand,
- one improvement you would make next.

## Privacy and safety

Use non-sensitive CSV files. The app processes uploaded data in the running app; do not upload private student, financial, or personal records to a public demo.
