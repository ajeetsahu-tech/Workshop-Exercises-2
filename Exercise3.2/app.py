"""Anonymous workshop feedback explorer."""

from pathlib import Path
from html import escape

import pandas as pd
import streamlit as st

from feedback_utils import load_feedback

st.set_page_config(page_title="Workshop Feedback Explorer", page_icon="📊", layout="wide")
st.title("Workshop Feedback Explorer")
st.caption("Explore anonymous, synthetic participant feedback by session and rating.")

DEFAULT_CSV = Path(__file__).with_name("feedback.csv")
uploaded = st.file_uploader("Upload a feedback CSV (optional)", type=["csv"])

try:
    feedback, notices = load_feedback(uploaded if uploaded is not None else DEFAULT_CSV)
except (OSError, ValueError) as error:
    st.error(str(error))
    st.info("Required columns: session, rating, topic_category. The comment column is optional.")
    st.stop()

for notice in notices:
    st.warning(notice)

if feedback.empty:
    st.warning("No valid responses to summarize. Check the CSV data and try again.")
    st.stop()

session_options = sorted(feedback["session"].dropna().unique().tolist())
with st.sidebar:
    st.header("Filters")
    selected_sessions = st.multiselect("Session", session_options, default=session_options)
    rating_range = st.slider("Rating range", min_value=1, max_value=5, value=(1, 5), step=1)

filtered = feedback[
    feedback["session"].isin(selected_sessions)
    & feedback["rating"].between(rating_range[0], rating_range[1])
].copy()

metric_a, metric_b, metric_c = st.columns(3)
metric_a.metric("Total responses", len(filtered))
metric_b.metric("Mean rating", f"{filtered['rating'].mean():.2f}" if not filtered.empty else "—")
metric_c.metric("Sessions represented", filtered["session"].nunique())

left, right = st.columns(2)
with left:
    st.subheader("Rating distribution")
    distribution = filtered["rating"].value_counts().reindex(range(1, 6), fill_value=0).rename_axis("Rating").to_frame("Responses")
    st.bar_chart(distribution)
with right:
    st.subheader("Average rating by session")
    session_means = filtered.groupby("session")["rating"].mean().sort_values(ascending=False)
    st.bar_chart(session_means)

st.subheader("Low-rated sessions")
if filtered.empty:
    st.write("No records match the current filters.")
else:
    session_summary = filtered.groupby("session").agg(responses=("rating", "size"), mean_rating=("rating", "mean"))
    low_rated = session_summary[session_summary["mean_rating"] < 3.0].sort_values("mean_rating")
    if low_rated.empty:
        st.success("No session averages below 3.0 in the filtered records.")
    else:
        st.dataframe(low_rated.style.format({"mean_rating": "{:.2f}"}), width="stretch")

st.subheader("Filtered feedback")
st.caption(f"Showing {len(filtered)} of {len(feedback)} valid responses.")
show_comments = st.checkbox("Show optional comments", value=True)
display_columns = ["session", "rating", "topic_category"] + (["comment"] if show_comments else [])
st.dataframe(filtered[display_columns], hide_index=True, width="stretch")
if show_comments:
    # Render comments as escaped plain text; never interpret uploaded text as HTML.
    comments = [escape(str(value)) for value in filtered["comment"] if str(value).strip()]
    if comments:
        with st.expander("Comments as safe plain text"):
            for comment in comments:
                st.text(comment)

st.download_button(
    "Download filtered records as CSV",
    data=filtered[display_columns].to_csv(index=False).encode("utf-8"),
    file_name="filtered_workshop_feedback.csv",
    mime="text/csv",
    disabled=filtered.empty,
)
st.caption("Feedback is synthetic and anonymous. Do not add names, email addresses, or other identifiers.")
