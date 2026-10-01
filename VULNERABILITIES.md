# Vulnerability Report

_Last updated: 2026-10-01 09:37 UTC_

Generated from the HEAD-of-default-branch SBOM of each tracked repo, scanned by Grype and Trivy. Only vulnerabilities with an upstream fix available are included. Per-repo JSON with the full finding detail is in [`vulns/`](vulns/).

## Summary

| Repo | Critical | High | Medium | Low | Negligible | Unknown |
|------|---|---|---|---|---|---|
| `demo.mahocommerce.com` | — | — | — | — | — | — |
| `directory-data` | — | — | — | — | — | — |
| `docker-images` | — | — | — | — | — | — |
| `icons` | — | — | — | — | — | — |
| `infrastructure` | — | — | — | — | — | — |
| `maho` | — | — | — | — | — | — |
| `maho-composer-patches` | — | — | — | — | — | — |
| `maho-composer-plugin` | — | — | — | — | — | — |
| `maho-l10n` | — | — | — | — | — | — |
| `maho-phpstan-plugin` | — | — | — | — | — | — |
| `maho-sample-data` | — | — | — | — | — | — |
| `maho-starter` | — | — | — | — | — | — |
| `mahocommerce.com` | — | — | — | — | — | — |
| `module-braintree` | — | — | — | — | — | — |
| `module-mcrypt-compat` | — | — | — | — | — | — |
| `module-mollie` | — | — | — | — | — | — |
| `module-netseasy` | — | — | — | — | — | — |
| `module-przelewy24` | — | — | — | — | — | — |
| `module-revolut` | — | — | — | — | — | — |
| `module-royalmail` | — | — | — | — | — | — |
| `module-taler` | — | — | — | — | — | — |
| `module-template` | — | — | — | — | — | — |
| `phpstorm` | — | — | — | — | — | — |
| `vscode` | — | 4 | 2 | — | — | — |
| `zed` | — | — | — | — | — | — |
| **Total** | — | **4** | **2** | — | — | — |

## Critical findings

_None._

## High findings

### `vscode`

- [CVE-2026-102276](https://nvd.nist.gov/vuln/detail/CVE-2026-102276) in `brace-expansion@5.0.9` — fix: `5.0.10, 3.0.7, 2.1.5, 1.1.19` (via trivy)
- [CVE-2026-102278](https://nvd.nist.gov/vuln/detail/CVE-2026-102278) in `brace-expansion@5.0.9` — fix: `5.0.11, 3.0.8, 2.1.6, 1.1.20` (via trivy)
- [GHSA-6j4f-fj2g-mc7p](https://github.com/advisories/GHSA-6j4f-fj2g-mc7p) in `brace-expansion@5.0.9` — fix: `5.0.10` (via grype)
- [GHSA-qhr7-859c-m2p7](https://github.com/advisories/GHSA-qhr7-859c-m2p7) in `brace-expansion@5.0.9` — fix: `5.0.11` (via grype)

