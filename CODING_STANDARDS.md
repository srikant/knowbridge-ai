# Coding Standards — KnowBridge AI

These standards apply to backend Python, frontend TypeScript/React, tests, configuration, documentation, and AI integrations.

## 1. General principles

- Favor clarity, correctness, security, and maintainability over cleverness.
- Keep modules focused and functions small enough to test.
- Use explicit names, types, and contracts. Avoid hidden global state and implicit provider selection.
- Do not introduce abstractions without a current use case; do create clear seams around external services.
- Keep the core app runnable without optional AI frameworks or external infrastructure.
- Document limitations honestly. Roadmap items are not current features.

## 2. Python and FastAPI

- Target Python 3.11+.
- Follow PEP 8; use four spaces for indentation and descriptive `snake_case` names.
- Add type hints to public functions, service boundaries, and nontrivial data structures.
- Use Pydantic models for validated API request/response payloads where appropriate.
- Keep HTTP routing thin: validate input, call a service, translate expected errors into appropriate HTTP responses.
- Keep business logic out of route handlers when it can be tested independently.
- Use `async def` when awaiting async I/O. Do not block the event loop with synchronous network or long-running CPU work inside async routes.
- Use explicit timeouts for outbound HTTP/model calls and bounded retry behavior where appropriate.
- Return stable, documented response shapes. Do not expose stack traces, secrets, local paths, or internal provider errors to clients.
- Use `HTTPException` or project-specific exceptions for expected failures; avoid broad exception handlers that silently hide errors.
- Use parameterized database queries. Keep database initialization and access patterns centralized.
- Keep secrets/configuration in environment-based settings, with safe defaults and validation.

## 3. TypeScript and React

- Use TypeScript for frontend code; avoid `any`. If unavoidable at an external boundary, narrow the type immediately and document why.
- Follow the existing React functional-component and hooks conventions.
- Use `PascalCase` for components/types and `camelCase` for variables/functions.
- Keep API calls in a small, reusable client/service layer instead of scattering fetch logic across components.
- Define explicit types for API responses and errors. Keep them aligned with FastAPI schemas.
- Handle loading, empty, success, and error states for asynchronous actions.
- Avoid duplicated state that can be derived from existing state or props.
- Use stable keys when rendering lists and clean up effects/subscriptions where necessary.
- Do not place API keys or server secrets in `VITE_*` variables; frontend variables are public at build time.
- Preserve accessible labels, keyboard interaction, focus visibility, and meaningful button text.

## 4. API contracts and errors

- Keep endpoint paths, HTTP methods, status codes, and JSON fields stable unless a deliberate migration is requested.
- Validate all client-controlled values on the server, including upload metadata and query parameters.
- Use consistent error responses and actionable, non-sensitive messages.
- Add tests for success, invalid input, missing resources, dependency failure, and boundary conditions.
- Do not return a successful response when the requested operation failed or only partially completed unless the partial result is explicitly represented.

## 5. Documents, retrieval, and RAG

- Treat all uploaded files, extracted text, and retrieved passages as untrusted data.
- Validate allowed extensions, content signatures where practical, file sizes, and extracted-text limits. Never trust the filename or client MIME type alone.
- Use safe temporary-file handling and avoid path traversal. Sanitize display names without losing the original source metadata needed for citations.
- Keep chunking deterministic and testable; define chunk size and overlap explicitly.
- Preserve document ID, chunk ID, source filename, and relevant page/offset metadata through ingestion and retrieval.
- Apply access filters before retrieval when user/tenant authorization is implemented; never rely on the LLM to enforce access boundaries.
- Prefer retrieval evidence over model memory. If evidence is insufficient, say so rather than fabricating an answer.
- Citations must point only to retrieved source chunks and should be independently testable.
- Test lexical and semantic retrieval using a small, versioned dataset with known relevant passages.

## 6. LLM providers and prompting

- Keep provider SDK code behind a provider/service interface. Route and UI code must not call provider SDKs directly.
- Make model provider, model name, timeout, and relevant limits configurable through backend settings.
- Do not log API keys, authorization headers, raw confidential documents, or unnecessary personally identifiable information.
- Bound prompt size, output tokens, tool calls, execution time, and retries.
- Validate structured model outputs against a schema before using them.
- Treat model output as untrusted input. Escape or validate content before rendering or passing it to other systems.
- Do not allow document text to override system instructions or expand tool permissions.
- Make provider fallback behavior explicit and observable; do not silently imply a generated answer was returned when only source excerpts were returned.
- Keep tests deterministic by injecting fake model providers; live provider tests must be opt-in.

## 7. Agent workflows and tools

- Prefer a bounded workflow over an open-ended autonomous agent when the task can be represented as explicit steps.
- Define graph state, node responsibilities, transitions, termination conditions, maximum steps, and failure paths.
- Validate every tool's input and output. Apply least privilege and explicit allowlists.
- Require human confirmation before consequential external actions or destructive operations.
- Make retries idempotent where possible; prevent duplicate side effects.
- Log tool names, durations, and outcome categories without leaking secrets or sensitive document contents.
- Test normal flow, tool failure, malformed output, timeouts, iteration limits, and prompt-injection attempts.

## 8. Dependencies and architecture

- Keep `backend/requirements.txt` limited to dependencies required for the core application.
- Put optional packages in the corresponding `requirements-*.txt` group and document installation commands.
- Pin or constrain dependency versions intentionally; avoid unbounded `latest` dependencies in reproducible builds.
- Do not install multiple frameworks that duplicate the same capability into the default path without a documented reason.
- Wrap vector stores, embedding providers, LLMs, and observability tools behind small interfaces where it enables testing or swapping implementations.
- Keep integration readiness distinct from connectivity checks and feature-level integration tests.
- Keep frontend and backend configuration separate; never leak server-only configuration to the browser.

## 9. Security and privacy

- Never commit `.env`, credentials, tokens, local databases containing user data, uploaded documents, or model weights.
- Validate and limit uploads and requests. Use safe file names and parameterized SQL.
- Configure CORS narrowly for deployment; do not treat permissive local development CORS as a production policy.
- Add authentication and per-document authorization before exposing the app to multiple users or the public internet.
- Do not claim tenant isolation until database, retrieval, deletion, and cache paths enforce and test it.
- Treat prompt injection, malicious files, oversized inputs, denial-of-service, and data leakage as explicit threat cases.
- Avoid storing full prompts/completions in observability platforms by default when they may contain private documents; configure redaction and retention deliberately.

## 10. Tests and quality gates

- Add or update tests with each behavior change.
- Backend test command, from `backend/`: `python -m pytest -q`.
- Frontend production build, from `frontend/`: `npm run build`.
- Run `git diff --check` and inspect the final diff before completion.
- Unit tests must not require internet access or paid services.
- Keep integration tests separate and document their prerequisites.
- Test API contracts, document validation, retrieval/citation behavior, provider selection, and expected failure paths.
- Do not weaken or delete a test solely to make a change pass; explain and justify any intentional contract change.

## 11. Documentation and configuration

- Update `README.md` when install steps, endpoints, features, architecture, or known limitations change.
- Update `.env.example` for new configuration, using placeholders only.
- Explain optional dependency groups and external services before asking users to install them.
- Include reproducible commands and expected outcomes in setup documentation.
- Keep architecture diagrams and feature lists aligned with code that actually exists.

## 12. Naming and formatting quick reference

| Area | Convention |
|---|---|
| Python functions/variables | `snake_case` |
| Python classes | `PascalCase` |
| TypeScript variables/functions | `camelCase` |
| React components/types | `PascalCase` |
| Constants | `UPPER_SNAKE_CASE` when truly constant |
| Environment variables | `UPPER_SNAKE_CASE` |
| API paths | lowercase, resource-oriented paths |
| Tests | name after behavior, e.g. `test_upload_rejects_unsupported_file` |

When an existing convention differs, avoid unrelated mass-renaming. Follow the local pattern unless it conflicts with security, correctness, or an explicitly agreed standard.
