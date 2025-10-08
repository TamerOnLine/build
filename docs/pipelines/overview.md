
**`docs/pipelines/overview.md`**
```markdown
# Pipelines Overview

We model the resume workflow as five reliable stages:

1. **Input**: schema validation & normalization
2. **View**: lightweight preview (fast PDF render)
3. **Save**: persist profile/settings (mock or real)
4. **Fetch**: retrieve profile/settings
5. **Print**: final high-quality PDF build

Each stage has pytest markers and CI jobs. See the full E2E: [pipelines/e2e.md](e2e.md).
