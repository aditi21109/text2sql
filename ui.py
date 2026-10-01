from decimal import Decimal

import pandas as pd
import streamlit as st

from app.config import settings
from app.pipeline import answer

st.set_page_config(page_title="Text-to-SQL", page_icon="🔎", layout="wide")
st.title("🔎 Text-to-SQL Assistant")
st.caption("Ask questions in plain English. Ambiguous questions get a clarifying question first.")

ss = st.session_state
ss.setdefault("base", "")
ss.setdefault("clarifs", [])
ss.setdefault("rounds", 0)
ss.setdefault("result", None)
ss.setdefault("error", None)


def run():
    """Base question + clarifications ko jodke pipeline chalao."""
    question = ss.base
    if ss.clarifs:
        question += "\n" + "\n".join(ss.clarifs)
    ss.error = None
    try:
        with st.spinner("Thinking..."):
            ss.result = answer(question)
    except Exception as e:
        ss.result = None
        ss.error = str(e)


def start(q: str):
    ss.base, ss.clarifs, ss.rounds = q.strip(), [], 0
    if ss.base:
        run()


def clean(v):
    return float(v) if isinstance(v, Decimal) else v


# ---------- Sidebar: example questions ----------
with st.sidebar:
    st.header("Try these")
    examples = [
        "How many customers are from India?",
        "Show recent orders",
        "Total revenue by country",
        "Who are our best customers?",
        "Top 5 products by quantity sold",
        "Delete cancelled orders",
        "What is the weather today?",
    ]
    for ex in examples:
        st.button(ex, on_click=start, args=(ex,), use_container_width=True)

# ---------- Question box ----------
with st.form("ask_form"):
    q = st.text_input("Your question", placeholder="e.g. Total revenue by country")
    submitted = st.form_submit_button("Ask")
if submitted:
    start(q)

# ---------- Results ----------
if ss.error:
    st.error(f"Something went wrong: {ss.error}")
    st.info("Agar 429 / rate limit error hai to 30 second ruk ke dobara try karo.")

res = ss.result
if res:
    if res.status == "ok":
        st.subheader("Generated SQL")
        st.code(res.sql, language="sql")

        if res.assumptions:
            st.subheader("Assumptions made")
            for a in res.assumptions:
                st.markdown(f"- {a}")

        st.subheader(f"Result ({len(res.rows)} rows)")
        if res.rows:
            rows = [[clean(v) for v in r] for r in res.rows]
            st.dataframe(pd.DataFrame(rows, columns=res.columns), use_container_width=True)
        else:
            st.info("Query ran fine but returned no rows.")

    elif res.status == "needs_clarification":
        if ss.rounds >= settings.max_clarify_rounds:
            st.warning("Question abhi bhi clear nahi hai. Please usse thoda aur specific karke dobara poochho.")
        else:
            st.info("🤔 " + res.message)
            with st.form("clarify_form"):
                answers = []
                for i, amb in enumerate(res.clarifying_questions):
                    st.markdown(f"**{amb.question}**")
                    choice = None
                    if amb.options:
                        choice = st.radio("Pick one", amb.options, key=f"r{ss.rounds}_{i}",
                                          label_visibility="collapsed")
                    typed = st.text_input("Or type your own answer", key=f"t{ss.rounds}_{i}")
                    answers.append((amb.phrase, typed.strip() or choice or ""))
                go = st.form_submit_button("Continue")
            if go:
                for phrase, a in answers:
                    if a:
                        ss.clarifs.append(f"Clarification - '{phrase}': {a}")
                ss.rounds += 1
                run()
                st.rerun()

    elif res.status == "refused":
        st.warning(res.message)

    else:
        st.error(res.message)