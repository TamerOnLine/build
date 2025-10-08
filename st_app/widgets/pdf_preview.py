from __future__ import annotations
import base64
import streamlit as st

def show_pdf_download(pdf_bytes: bytes, filename: str = "resume.pdf") -> None:
    """
    Display a download button and optional inline PDF preview.

    Parameters
    ----------
    pdf_bytes : bytes
        The PDF content to be downloaded.
    filename : str, optional
        Suggested filename for download (default: 'resume.pdf').
    """
    if not pdf_bytes:
        st.warning("⚠️ No PDF data available to download.")
        return

    # Encode once for preview
    b64 = base64.b64encode(pdf_bytes).decode("ascii")

    st.download_button(
        "⬇️ Download PDF",
        data=pdf_bytes,
        file_name=filename,
        mime="application/pdf",
        key="btn_download_pdf",
    )

    with st.expander("Preview (experimental)"):
        st.markdown(
            f"""
            <iframe
                src="data:application/pdf;base64,{b64}"
                style="width:100%;height:80vh;border:none;"
            ></iframe>
            """,
            unsafe_allow_html=True,
        )
