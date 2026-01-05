import streamlit as st
import pandas as pd
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import os

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(
    page_title="NLP Report Generator",
    layout="wide"
)

st.title("📄 NLP Trending Topics Report Generator")
st.write("Generate an ASCII-safe NLP PDF report from trending news data.")

# =================================================
# TEXT SANITIZER (CRITICAL)
# =================================================
def sanitize_text(text):
    if not isinstance(text, str):
        return ""

    replacements = {
        "₹": "Rs",
        "–": "-",
        "—": "-",
        "’": "'",
        "‘": "'",
        "“": '"',
        "”": '"'
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    return text.encode("latin-1", "ignore").decode("latin-1")

# =================================================
# PDF CLASS
# =================================================
class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 11)
        self.cell(
            0, 10,
            "Trending Topics NLP Analysis Report",
            align="C",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT
        )

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", size=8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

# =================================================
# LOAD DATA (FROM REPO)
# =================================================
@st.cache_data
def load_data():
    df = pd.read_csv("trending_topics.csv")
    word_freq = pd.read_csv("word_frequency_table.csv")
    return df, word_freq

try:
    df, word_freq = load_data()
except Exception as e:
    st.error("CSV files not found or invalid.")
    st.stop()

# =================================================
# DATA PREVIEW
# =================================================
st.subheader("📊 Data Preview")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Trending Topics**")
    st.dataframe(df.head())

with col2:
    st.markdown("**Word Frequency**")
    st.dataframe(word_freq.head(10))

# =================================================
# PDF GENERATION
# =================================================
st.subheader("📄 Generate PDF Report")

if st.button("Generate PDF"):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    usable_width = pdf.w - pdf.l_margin - pdf.r_margin

    # -------- COVER --------
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(
        0, 20,
        "NLP Based Trending Topics Report",
        align="C",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT
    )

    pdf.ln(10)
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(
        usable_width,
        8,
        sanitize_text(
            "This report presents an end to end Natural Language Processing analysis "
            "of trending news data using API based collection, TF IDF analysis, and "
            "statistical techniques."
        )
    )

    # -------- EXECUTIVE SUMMARY --------
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(
        0, 10,
        "Executive Summary",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT
    )

    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(
        usable_width,
        7,
        sanitize_text(
            f"- Total articles analyzed: {len(df)}\n"
            "- Finance, sports, and global news dominate trends\n"
            "- TF IDF highlights article specific relevance"
        )
    )

    # -------- WORD FREQUENCY --------
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(
        0, 10,
        "Word Frequency Analysis",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT
    )

    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(usable_width * 0.6, 8, "Word", border=1)
    pdf.cell(usable_width * 0.4, 8, "Frequency", border=1)
    pdf.ln()

    pdf.set_font("Helvetica", size=10)
    for _, row in word_freq.head(20).iterrows():
        pdf.cell(
            usable_width * 0.6,
            8,
            sanitize_text(row["word"]),
            border=1
        )
        pdf.cell(
            usable_width * 0.4,
            8,
            str(row["frequency"]),
            border=1
        )
        pdf.ln()

    # -------- APPENDIX --------
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(
        0, 10,
        "Appendix: Top Headlines",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT
    )

    pdf.set_font("Helvetica", size=10)
    for title in df["title"]:
        pdf.multi_cell(
            usable_width,
            6,
            "- " + sanitize_text(title)
        )

    # SAVE PDF
    pdf_path = "BEST_ASCII_SAFE_NLP_REPORT.pdf"
    pdf.output(pdf_path)

    st.success("PDF generated successfully!")

    with open(pdf_path, "rb") as f:
        st.download_button(
            label="⬇️ Download PDF",
            data=f,
            file_name=pdf_path,
            mime="application/pdf"
        )
