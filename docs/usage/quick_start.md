# Quick Start

1. Install:
   ```bash
   python -m pip install -r requirements/requirements.build.txt
    ```

2. Validate a minimal flow:
   ```bash
    pytest -q -m "view"
    ```

2. Build a final PDF locally:
   ```bash
    from api.pdf_utils.fonts import register_all_fonts
    from api.pdf_utils.builder import build_resume_pdf
    register_all_fonts()
    payload = {"profile": {"header":{"name":"Tamer","title":"Software Dev"}}, "theme_name":"aqua-card","ui_lang":"en","layout_inline":{"flow":[]}}
    pdf = build_resume_pdf(data=payload)
    open("resume.pdf","wb").write(pdf)

    ```