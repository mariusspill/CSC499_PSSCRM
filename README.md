# Measuring the Adoption of Software Supply Chain Security Practices in Public Open-Source Projects

Empirical analysis pipeline for measuring the adoption of software supply chain security practices across public open-source repositories using large-scale GitHub data.

The project focuses on extracting, transforming, and analyzing historical repository activity to identify how widely security-oriented engineering practices are adopted in real-world OSS ecosystems.

---

## Overview

Modern software supply chain attacks increasingly target development workflows rather than application code itself. While frameworks such as SLSA and recommendations from organizations like OpenSSF and CISA promote stronger engineering practices, there is still limited empirical data on how broadly these practices are adopted across open-source software.

This project builds a reproducible data engineering and analytics pipeline to measure adoption trends at scale.

Current focus areas include:

- Multi-party code review adoption
- Repository hygiene and binary artifact avoidance
- Historical repository evolution
- Large-scale GitHub metadata processing
- Security-oriented OSS analytics

---

# Objectives

The project aims to:

- Build a reusable repository analysis pipeline
- Create structured datasets from public GitHub repositories
- Measure adoption of selected SSCSP indicators over time
- Analyze differences across:
  - programming languages
  - project size
  - activity level
  - ecosystem maturity
- Produce reproducible visualizations and findings

---

# Core Research Variables

## 1. Multi-Party Code Review Adoption

Measures whether repositories use structured pull request review workflows involving multiple contributors or reviewers.

Potential indicators include:

- Pull request review events
- Number of reviewers per PR
- Approval requirements
- Merge patterns
- Branch protection implications

### Data Sources

- GitHub REST API
  
---

## 2. Binary Artifact Avoidance

Measures whether repositories avoid committing compiled binaries or generated artifacts directly into version control.

Potential indicators include:

- Presence of:
  - `.jar`
  - `.exe`
  - `.dll`
  - `.class`
  - compressed archives
  - generated build outputs
- Repository size anomalies
- Artifact frequency over time

This variable acts as a proxy for repository hygiene and traceability.

---

# Architecture

```text
                ┌────────────────────┐
                │   GitHub APIs      │
                └─────────┬──────────┘
                          │
                   Data Ingestion
                          │
                ┌─────────▼──────────┐
                │ Raw Repository Data│
                └─────────┬──────────┘
                          │
                    ETL / Cleaning
                          │
                ┌─────────▼──────────┐
                │ Structured Dataset │
                └─────────┬──────────┘
                          │
               Statistical / Trend Analysis
                          │
                ┌─────────▼──────────┐
                │ Research Findings  │
                └────────────────────┘
```

---

# Tech Stack

## Data Engineering

- Python
- SQL

## Data Collection

- GitHub REST API

## Analytics & Visualization

- SQL Views

## Reproducibility

- Git
- Virtual environments
- Deterministic pipelines
- Config-driven workflows

---


# Example Research Questions

- How common is multi-party code review in OSS projects?
- Does SSCSP adoption correlate with repository popularity?
- Which ecosystems show stronger security-oriented workflows?
- Are larger repositories more likely to avoid binary artifacts?
- How do practices evolve over repository lifetime?

---

# Data Pipeline Goals

This repository is intentionally structured more like a lightweight analytics platform than a one-off academic codebase.

Key engineering priorities include:

- Reproducibility
- Schema consistency
- Incremental processing
- Separation of raw and processed data
- Efficient columnar storage
- Scalable repository analysis
- Clear ETL boundaries

The project is designed to remain extensible as additional SSCSP indicators are added over time.

---

# Potential Future Extensions

Possible future metrics include:

- Signed commits
- CI/CD adoption
- Dependency pinning
- SBOM generation
- Provenance attestations
- Secret scanning indicators
- Branch protection rules
- Release signing

---

# Research Context

This project was developed as part of an undergraduate research project in computer science focused on empirical software engineering and software supply chain security.

The broader objective is to contribute reproducible measurements and engineering tooling that help quantify real-world adoption of secure development practices in the open-source ecosystem.

---

# Why This Repository Exists

Most discussions around software supply chain security are policy-heavy and measurement-light.

This repository attempts to bridge that gap through:

- Large-scale empirical analysis
- Reproducible engineering workflows
- Structured OSS datasets
- Practical security telemetry

The emphasis is not only on research findings, but also on building clean, scalable data infrastructure capable of supporting future OSS ecosystem analysis.

---

# License

Proprietary.

All rights reserved.

This repository and its contents may not be copied, modified, distributed, or used without explicit permission from the author.
