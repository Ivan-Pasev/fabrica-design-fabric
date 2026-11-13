# Security policy / responsible disclosure

Status: experimental reference code, not a production-grade renderer or sandbox. Do not use it to ingest untrusted code with elevated privileges.

- Keep source inputs and generated HTML/SVG untrusted until validated; reject script injection and path traversal.
- Avoid privileged Chrome. Upstream headless helpers may enable local-file access and disable Linux sandboxing; use OS/container isolation with network and filesystem limits.
- Do not embed credentials, local Drive IDs from private trees, personal information, tenant information or operational CodexStation secrets in public artifacts.
- The self-contained timeline uses fixed generated state snapshots, not eval/Function execution on user-supplied text.
- The installer requires explicit `--apply` and refuses pre-existing target paths, including when `--replace` is provided.
- Geometry tests are bounded numeric checks. Unexpected geometry, fonts, WebGL results or browsers must remain `INCONCLUSIVE` until audited.
- Report vulnerabilities privately to repository maintainers; do not post exploit data containing user information in public issues.
