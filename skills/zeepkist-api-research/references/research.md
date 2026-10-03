# Source, assets and live evidence

Record installed assembly hashes and snapshot identity before trusting a cached decompile. Methods named check_game_version, decompile_game, search_code or get_class_info may exist in a consumer's Zeepkist MCP; these are discovery hints, not a bundled interface or fixed invocation contract. Inspect the connected server's actual schema and local workflow.

If structured class parsing returns null while code search finds the type, inspect its source section and declaring assembly. Retain the parser limitation. Avoid repeated full decompile dumps and signatures inferred from older mods. Inspect inheritance, call sites and initialization order where relevant.

For integration planning, note return/parameter types, static/instance access, field/property distinction and availability in the relevant scene. Reflection adapters need shape checks and appropriate fallback on contract drift. Compiling against a repository SDK does not establish installed SDK compatibility. Use installed build evidence and relevant [BepInEx troubleshooting guidance](https://docs.bepinex.dev/articles/user_guide/troubleshooting.html) when loader/dependency evidence matters.

Code refresh does not update an asset catalog. A missing block ID can reflect stale/incomplete capture. Establish catalog version/hash, capture scene/context and actual enumeration of the requested ID. Keep assets and decompiled code local according to consumer reuse permissions.

A bridge timeout without an available game/session does not establish protocol incompatibility. Inspect bridge availability/current scene only when a live check is in scope. Preserve a running editor fixture or driving session. Report unavailable runtime checks explicitly; offline search can still be useful.

Deliver separate conclusions for source contract, catalog coverage and live behavior. No one tier substitutes for the others.
