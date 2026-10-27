# PDF to CSV Converter

A Streamlit app that extracts tables from text-based PDFs, lets you preview and
edit the results, and downloads the selected table as a CSV file.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Upload a PDF containing selectable text. Scanned PDFs require OCR and are not
currently supported.

## Deploy on Streamlit Community Cloud

1. Push this repository to GitHub.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with
   GitHub and authorize access to this repository.
3. Create an app from this repository, select the `main` branch, and set
   `app.py` as the main file.
4. Deploy the app and use the generated URL to open it.

Uploaded PDFs are processed by the server running the deployed app. Avoid
uploading documents containing sensitive information unless you trust the
deployment and its access controls.
