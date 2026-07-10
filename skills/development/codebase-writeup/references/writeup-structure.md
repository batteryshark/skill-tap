# Writeup structure

Adapt the depth to the audience. Omit sections that do not apply rather than padding them.

## Scope and method

State the repository revision or local state, requested focus, areas read closely, areas sampled, commands run, and important limitations.

## What this project is

Explain the user or operator problem, primary runtime, main entry point, and the most important technical fact in a short opening.

## Technical foundation

Summarize languages, frameworks, runtime, build system, package management, storage, deployment shape, and version evidence. Call out meaningful mismatches or legacy constraints.

## System map

Describe major modules and ownership boundaries. Trace control and data through at least one representative execution path. Explain where configuration, state, I/O, and side effects enter.

## Getting started and safe change

For onboarding or handoff deliverables, provide the shortest evidence-backed path from checkout to a successful verification. Point to common change locations, their tests, generated boundaries, and any compatibility or operational constraint a contributor must not discover by accident.

## External boundaries

Describe APIs, databases, queues, filesystems, platform services, SDKs, and remote domains. Explain what each boundary is used for and how failures or data shapes are translated.

## Distinctive behavior

Give each important or surprising capability a descriptive subsection. Lead with the behavior, cite the implementation, then explain the operational or user impact. Distinguish reachable behavior from unused, gated, or speculative code.

## Reliability, security, and privacy

Include this section only to the depth authorized and supported. Describe failure handling, sensitive-data boundaries, permissions, credential locations by type, transport, persistence, and trust assumptions. Separate confirmed issues from review leads.

## Gaps and open questions

List missing tests, dead or unfinished paths, undocumented operations, version uncertainty, and areas that need runtime validation or owner context.

## Takeaway

Summarize the system's shape, strongest evidence-backed finding, and the highest-value next investigation in a few direct paragraphs.
