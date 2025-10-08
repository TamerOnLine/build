# CI: Matrix per Block

- Discovers block IDs from `api/pdf_utils/blocks/*.py`.
- Runs a smoke test per block → builds a tiny PDF per block.
- Artifacts: `out/smoke_<block>.pdf`.

See workflow file: `.github/workflows/ci-blocks.yml`.
