---
name: zeepkist-api-research
description: Research exact installed Zeepkist game or mod API contracts and diagnose stale code, asset catalog or bridge evidence. Use before native integration changes or to investigate symbols after game updates; offline research does not establish live gameplay acceptance.
---

# Zeepkist API research

Establish the relevant contract from the consumer's installed binaries and tools, with code, asset and runtime findings distinguished. This skill supplies no game assemblies, decompiled source, catalog, MCP server or in-game bridge.

## Resolve the evidence source

Inspect project instructions and available research tools. Resolve game/install and research workspace paths, installed version/assembly digests, loader/SDK versions, requested symbols and output location using [inputs.md](references/inputs.md). Keep values and their origins explicit; the example record contains unresolved inputs.

Check whether searchable source was generated from those installed assemblies. If stale, use the consumer's maintained refresh/decompiler workflow for the relevant assemblies when within the request's scope. Preserve unrelated work and record the version/hash after refresh. An unavailable refresh leaves the result scoped to the existing snapshot, not the current installation.

## Find the relevant contract

Start with a targeted class/member query and inspect its declaring type, signature, visibility, overloads and relevant caller/lifecycle conditions. Use current tool schemas rather than assuming server namespaces, argument names, assembly lists or a fixed tool count. Read [research.md](references/research.md) for parser fallback and runtime/asset distinctions.

A null class-info result is not proof a symbol is absent. If the consumer's tool provides code search, inspect a bounded exact-name search and source context before attributing absence to the installed API. Distinguish fields from properties, static from instance members, editor from test-drive/gameplay contexts and optional providers from native fallbacks.

## Report the usable result

Report installed version/digests, source snapshot currency, exact symbol evidence, required lifecycle/context conditions, uncertainty and the smallest next check. Label decompiled behavior as source evidence. A compile check establishes signature compatibility in that build context; runtime, rendering, human input and multiplayer behavior need applicable live evidence.

For block/material/asset questions, establish separate catalog identity and capture context. For a live request, inspect available bridge/session state first and preserve active work. Use only live actions authorized by the task; research does not authorize loading a level, installing a mod or manipulating a lobby.
