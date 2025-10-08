# End-to-End Flow (Input → View → Save → Fetch → Print)

- Pytest markers:
  - `@pytest.mark.input`, `@pytest.mark.view`, `@pytest.mark.save`, `@pytest.mark.fetch`, `@pytest.mark.print`
- CI runs coverage and uploads PDFs as artifacts.
- Swap `save/fetch` mock with real FastAPI routes when ready.
