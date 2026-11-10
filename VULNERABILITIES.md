# Vulnerability Report

_Last updated: 2026-11-10 10:47 UTC_

Generated from the HEAD-of-default-branch SBOM of each tracked repo, scanned by Grype and Trivy. Only vulnerabilities with an upstream fix available are included. Per-repo JSON with the full finding detail is in [`vulns/`](vulns/).

## Summary

| Repo | Critical | High | Medium | Low | Negligible | Unknown |
|------|---|---|---|---|---|---|
| `demo.mahocommerce.com` | — | — | — | — | — | — |
| `directory-data` | — | — | — | — | — | — |
| `docker-images` | — | — | — | — | — | — |
| `icons` | — | — | — | — | — | — |
| `infrastructure` | — | 1 | — | 1 | — | — |
| `maho` | — | — | — | — | — | — |
| `maho-composer-patches` | — | — | — | — | — | — |
| `maho-composer-plugin` | — | — | — | — | — | — |
| `maho-l10n` | — | — | — | — | — | — |
| `maho-phpstan-plugin` | — | — | — | — | — | — |
| `maho-sample-data` | — | — | — | — | — | — |
| `maho-starter` | — | — | — | — | — | — |
| `mahocloud-docker-images` | — | — | — | — | — | — |
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
| `vscode` | — | — | 2 | — | — | — |
| `zed` | — | — | — | — | — | — |
| **Total** | — | **1** | **2** | **1** | — | — |

## Critical findings

_None._

## High findings

### `infrastructure`

- [CVE-2026-121971](https://nvd.nist.gov/vuln/detail/CVE-2026-121971) in `symfony/http-client@v8.1.10` — fix: `5.4.0, 6.2.0, 8.1.0, 8.1.11, 5.2.0, 6.4.0, 7.3.0, 7.4.23, 4.4.0, 6.1.0, 6.3.0, 6.4.50, 7.4.0, 5.0.0, 5.3.0, 5.4.56, 7.1.0, 7.2.0, 5.1.0` (via trivy)

