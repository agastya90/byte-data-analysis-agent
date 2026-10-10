import re
import pandas as pd
import streamlit as st

st.set_page_config(page_title="DataBuddy — CSV Analysis Agent", page_icon="📊", layout="wide")
st.title("📊 DataBuddy — Data Analysis Agent")
st.write("Upload a CSV, ask a question in plain English, and DataBuddy will choose a real analysis tool.")

def dataset_summary(df):
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "data_types": {str(k): str(v) for k, v in df.dtypes.items()},
    }

def missing_values(df):
    result = df.isna().sum()
    return result[result > 0].sort_values(ascending=False).to_frame("missing_values") if (result > 0).any() else "No missing values found."

def top_rows(df, n=5, largest=True):
    numeric = df.select_dtypes(include="number").columns.tolist()
    if not numeric:
        return "I couldn't find a numeric column to rank. Try asking for a summary or missing values."
    col = numeric[0]
    return df.nlargest(n, col) if largest else df.nsmallest(n, col)

def group_statistics(df, question):
    # Supports questions such as "average score by subject" or "sum sales by region".
    match = re.search(r"\b(average|mean|avg|sum|total|maximum|max|minimum|min|count)\b.*?\bby\s+([A-Za-z_][\w ]*)", question, re.I)
    if not match:
        return None
    operation = match.group(1).lower()
    group_text = match.group(2).strip(" ?.!").lower()
    group_col = next((c for c in df.columns if c.lower() == group_text), None)
    if group_col is None:
        group_col = next((c for c in df.columns if c.lower() in group_text or group_text in c.lower()), None)
    if group_col is None:
        return f"I couldn't identify the column after 'by'. Available columns: {', '.join(map(str, df.columns))}"
    numeric = df.select_dtypes(include="number").columns.tolist()
    if operation in ("count",):
        return df.groupby(group_col, dropna=False).size().to_frame("count")
    if not numeric:
        return "This operation needs at least one numeric column."
    value_col = next((c for c in numeric if c != group_col), numeric[0])
    fn = {"average": "mean", "mean": "mean", "avg": "mean", "sum": "sum", "total": "sum",
          "maximum": "max", "max": "max", "minimum": "min", "min": "min"}[operation]
    return df.groupby(group_col, dropna=False)[value_col].agg(fn).to_frame(f"{fn}_{value_col}")

def correlation_matrix(df):
    numeric = df.select_dtypes(include="number")
    if numeric.shape[1] < 2:
        return "Correlation needs at least two numeric columns."
    return numeric.corr(numeric_only=True).round(3)

def filter_rows(df, question):
    # Example: "show rows where score > 80" or "filter age <= 20"
    match = re.search(r"(?:where|with|filter(?: rows)?(?: where)?)\s+([A-Za-z_][\w ]*?)\s*(>=|<=|==|=|>|<)\s*(-?\d+(?:\.\d+)?)", question, re.I)
    if not match:
        return None
    col_text, op, value_text = match.groups()
    col_text = col_text.strip().lower()
    col = next((c for c in df.columns if c.lower() == col_text), None)
    if col is None:
        col = next((c for c in df.columns if c.lower() in col_text or col_text in c.lower()), None)
    if col is None:
        return f"Column '{col_text}' not found. Available columns: {', '.join(map(str, df.columns))}"
    try:
        series = pd.to_numeric(df[col], errors="raise")
    except (ValueError, TypeError):
        return f"Column '{col}' is not numeric, so numeric comparisons aren't supported for it."
    value = float(value_text)
    mask = {">": series > value, "<": series < value, ">=": series >= value,
            "<=": series <= value, "=": series == value, "==": series == value}[op]
    return df.loc[mask]

def answer_question(df, question):
    q = question.lower().strip()
    # Tool selection: the question determines which distinct analysis function runs.
    if any(word in q for word in ("missing", "null", "empty cells", "na values")):
        return "Tool used: missing_values", missing_values(df)
    if any(word in q for word in ("correlation", "correlated", "relationship between")):
        return "Tool used: correlation_matrix", correlation_matrix(df)
    filtered = filter_rows(df, q)
    if filtered is not None:
        return "Tool used: filter_rows", filtered
    grouped = group_statistics(df, q)
    if grouped is not None:
        return "Tool used: group_statistics", grouped
    if any(word in q for word in ("highest", "largest", "top", "maximum", "highest-scoring")):
        return "Tool used: top_rows", top_rows(df, largest=True)
    if any(word in q for word in ("lowest", "smallest", "bottom", "minimum")):
        return "Tool used: top_rows", top_rows(df, largest=False)
    if any(word in q for word in ("summary", "describe", "overview", "columns", "dataset", "data types", "how many rows")):
        return "Tool used: dataset_summary", dataset_summary(df)
    return ("No tool selected", "I couldn't match that question to a tool yet. Try: 'summary', 'show missing values', "
            "'top rows', 'lowest rows', 'average marks by subject', 'show rows where marks > 80', or 'correlation matrix'.")

st.sidebar.header("1. Upload data")
uploaded = st.sidebar.file_uploader("Choose a CSV file", type=["csv"])
if uploaded:
    try:
        df = pd.read_csv(uploaded)
    except Exception as exc:
        st.error(f"Couldn't read this CSV: {exc}")
        st.stop()
else:
    df = pd.DataFrame({
        "student": ["Asha", "Rohan", "Meera", "Kabir", "Zoya", "Ishaan"],
        "maths": [88, 72, 95, 61, 84, 77],
        "science": [91, 80, 89, 70, None, 86],
        "attendance": [96, 82, 98, 75, 91, 88],
        "section": ["A", "B", "A", "B", "A", "B"],
    })
    st.info("Showing demo data. Upload your own CSV from the sidebar to analyse another dataset.")

if df.empty:
    st.warning("This CSV has no data rows. Please upload a CSV with at least one row.")
    st.stop()

st.subheader("2. Preview your data")
st.dataframe(df.head(10), use_container_width=True)
st.caption(f"{len(df):,} rows · {len(df.columns)} columns")

st.subheader("3. Ask a question")
question = st.text_input("Your question", placeholder="e.g. show missing values, or average maths by section")
if st.button("Analyse", type="primary") and question.strip():
    tool_name, result = answer_question(df, question)
    st.markdown(f"**{tool_name}**")
    if isinstance(result, pd.DataFrame):
        st.dataframe(result, use_container_width=True)
    else:
        st.write(result)
    st.caption("Note: this beginner version uses transparent question matching, not an LLM. It calculates results from the uploaded data.")
