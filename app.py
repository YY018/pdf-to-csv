
from io import BytesIO
import re

import pandas as pd
import pdfplumber
import streamlit as st


st.set_page_config(
    page_title="PDF to CSV Converter",
    page_icon="📄",
    layout="wide",
)

st.title("📄 PDF to CSV Converter")
st.write(
    "Upload a PDF, extract its tables, preview the data, "
    "and download your selected table as a CSV file."
)

uploaded_file = st.file_uploader(
    "Upload your PDF",
    type=["pdf"],
    help="Choose a PDF containing selectable text or tables.",
)

if uploaded_file is not None:
    pdf_bytes = uploaded_file.getvalue()

    # Basic upload validation
    if not pdf_bytes.startswith(b"%PDF-"):
        st.error("This file does not appear to be a valid PDF.")
        st.stop()

    extracted_tables = []

    try:
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            st.info(f"PDF contains {len(pdf.pages)} page(s).")

            progress = st.progress(0)

            for page_number, page in enumerate(pdf.pages, start=1):
                tables = page.extract_tables()

                for table_number, rows in enumerate(tables, start=1):
                    # Remove completely empty rows
                    rows = [
                        row for row in rows
                        if row and any(
                            cell is not None and str(cell).strip()
                            for cell in row
                        )
                    ]

                    if not rows:
                        continue

                    # Ensure every row has the same number of columns
                    max_columns = max(len(row) for row in rows)

                    cleaned_rows = [
                        [
                            str(cell).strip() if cell is not None else ""
                            for cell in row
                        ] + [""] * (max_columns - len(row))
                        for row in rows
                    ]

                    extracted_tables.append({
                        "label": (
                            f"Page {page_number} — "
                            f"Table {table_number}"
                        ),
                        "rows": cleaned_rows,
                        "page": page_number,
                    })

                progress.progress(page_number / len(pdf.pages))

    except Exception as error:
        st.error(
            "Could not read this PDF. It may be corrupted, "
            "encrypted, or unsupported."
        )
        with st.expander("Technical details"):
            st.code(str(error))
        st.stop()

    if not extracted_tables:
        st.warning(
            "No tables were detected. This can happen with scanned "
            "PDFs or documents whose text is not arranged as tables."
        )
        st.write(
            "Try a PDF with selectable text. OCR support for scanned "
            "documents can be added separately."
        )
        st.stop()

    st.success(
        f"Found {len(extracted_tables)} table(s) across the PDF."
    )

    # Select which table to preview and export
    selected_index = st.selectbox(
        "Choose a table",
        options=list(range(len(extracted_tables))),
        format_func=lambda i: extracted_tables[i]["label"],
    )

    selected_table = extracted_tables[selected_index]
    rows = selected_table["rows"]

    st.subheader("Preview and clean your data")

    use_first_row = st.checkbox(
        "Use the first row as column headings",
        value=True,
        help=(
            "Uncheck this if the table has no header row. "
            "Generic column names will be used instead."
        ),
    )

    if use_first_row and len(rows) > 1:
        headers = [
            cell if cell else f"Column {i + 1}"
            for i, cell in enumerate(rows[0])
        ]
        dataframe = pd.DataFrame(rows[1:], columns=headers)
    else:
        dataframe = pd.DataFrame(rows)
        dataframe.columns = [
            f"Column {i + 1}"
            for i in range(dataframe.shape[1])
        ]

    # Make duplicate or blank column names easier to work with
    cleaned_columns = []
    seen = {}

    for column in dataframe.columns:
        name = str(column).strip() or "Unnamed"
        count = seen.get(name, 0)
        seen[name] = count + 1

        if count:
            name = f"{name}_{count + 1}"

        cleaned_columns.append(name)

    dataframe.columns = cleaned_columns

    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", len(dataframe))
    col2.metric("Columns", len(dataframe.columns))
    col3.metric("Source page", selected_table["page"])

    # Editable preview lets the user correct extraction mistakes
    edited_dataframe = st.data_editor(
        dataframe,
        num_rows="dynamic",
        use_container_width=True,
        key=f"editor_{selected_index}_{use_first_row}",
    )

    st.subheader("Export")

    csv_data = edited_dataframe.to_csv(
        index=False
    ).encode("utf-8-sig")

    default_name = re.sub(
        r"[^A-Za-z0-9_-]+",
        "_",
        uploaded_file.name.rsplit(".", 1)[0],
    ).strip("_") or "converted"

    st.download_button(
        label="⬇️ Download CSV",
        data=csv_data,
        file_name=f"{default_name}_table_{selected_index + 1}.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.caption(
        "Check the preview before downloading. PDF extraction can "
        "misalign cells or omit information. This app processes the "
        "uploaded file locally within the running app process; if you "
        "deploy it online, uploaded data is processed by that server."
    )

else:
    st.info("Upload a PDF above to get started.")

    with st.expander("How it works"):
        st.markdown(
            """
            1. Upload a PDF.
            2. Extract tables from each page.
            3. Choose a table and inspect its contents.
            4. Edit incorrect or missing values.
            5. Download the cleaned table as a CSV.
            """
        )
