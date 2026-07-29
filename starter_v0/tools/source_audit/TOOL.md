---
name: source_audit
track: core
kind: local_analysis
requires_env: []
inputs: [items, min_independent_sources]
outputs: [item_count, unique_domain_count, unique_domains, duplicate_urls, verdict, notes]
side_effect: false
---
# source_audit

Audits an existing list of research items for URL duplication and source-domain
diversity. It does not search the web or judge whether a claim is factually true.

Use it after items have already been collected. A result with multiple independent
domains is stronger evidence of source diversity, but it is not a substitute for
manual fact checking.
