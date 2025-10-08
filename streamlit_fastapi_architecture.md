# Streamlit vs FastAPI — Architecture Overview (Fixed Mermaid)

## Concept Summary

- **Streamlit talks to humans (UI).**  
- **FastAPI talks to machines (API).**

When combined, they form a **multi-interface system** — one backend serving multiple frontends.

---

## Case 1 — Streamlit Only

- The Streamlit app is the entire project (UI + logic).
- Users interact via the browser; the app generates the PDF locally.

```mermaid
graph TD
    A[User] -->|Interacts| B[Streamlit App]
    B -->|Calls local functions| C[PDF Builder]
    C --> D[Resume.pdf]
    B -->|Displays| A
```

---

## Case 2 — Streamlit + FastAPI

- FastAPI acts as the backend engine (API).
- Streamlit is one of many possible frontends.
- Any client (React, mobile, CLI, automation) can consume the API.

```mermaid
graph TD
    U[Human] -->|UI interaction| ST[Streamlit App]
    ST -->|POST JSON| API[FastAPI Server]
    API --> CORE[PDF Builder / Business Logic]
    CORE --> PDF[Resume.pdf]
    API -->|Response: PDF bytes| ST
    ST -->|Display or Download| U
```

---

## Layered Architecture (Professional Layout)

```mermaid
graph LR
    subgraph Frontend
        ST[Streamlit UI]
        REACT[React / Next.js]
        MOB[Mobile App]
    end

    subgraph Backend
        API[FastAPI Service]
    end

    subgraph Core
        BUILDER[PDF Builder]
        DB[(Database / Profiles Storage)]
    end

    ST --> API
    REACT --> API
    MOB --> API
    API --> BUILDER
    API --> DB
```

---

## Technical Breakdown

| Layer | Component | Role | Communicates With |
|--------|------------|------|------------------|
| Presentation (UI) | Streamlit / React / Mobile | Human interaction | FastAPI |
| Backend Service | FastAPI | Business logic, APIs | All frontends |
| Core Engine | PDF Builder (ReportLab / pdf_utils) | PDF generation | FastAPI / Streamlit |
| Storage | Database / JSON Profiles | Data persistence | FastAPI |

---

## Summary

| Approach | Description | Example Use |
|-----------|--------------|--------------|
| Streamlit Only | Single app that talks directly to users. | Local resume builder, dashboards |
| FastAPI + Streamlit | Frontend (Streamlit) + Backend (FastAPI) separation. | Public platform, multi-client system |
| FastAPI Only | Headless backend service for automation. | Integration into other systems |
