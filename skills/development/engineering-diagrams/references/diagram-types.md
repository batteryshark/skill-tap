# Diagram types

Choose the view from the question the reader needs answered.

| Type | Use it to answer | Include |
|---|---|---|
| System | What surrounds this system and where are its major boundaries? | Actors, system, stores, external systems, major entry points |
| Component | Which internal part owns each responsibility and dependency? | Components, owned data, interfaces, dependency direction |
| Data flow | Where does information originate, change, persist, and leave? | Sources, validation, transformations, stores, sinks, side effects |
| Sequence | What happens, in what order, for one runtime scenario? | Participants, ordered calls, responses, important alternatives and failures |
| State | Which states exist and what transitions are allowed? | Initial and terminal states, triggers, guards, invalid or uncertain transitions |
| Trust boundary | Where does trust or privilege change? | Actors, untrusted inputs, authentication, authorization, sensitive stores, external parties |

## Selection rules

- Use a system diagram for context and a component diagram for internal ownership. Do not combine them merely to save a file.
- Use a data-flow diagram when transformations and storage matter more than timing.
- Use a sequence diagram when ordering, retries, callbacks, or cross-component coordination matter.
- Use a state diagram when a status field, protocol, job, or lifecycle has transition rules.
- Use a trust-boundary diagram only from security-relevant evidence. A network hop is not automatically a trust boundary, and a process boundary may be one even on the same host.

## Evidence notation

Keep notation simple and explain it in a legend. A useful default is:

- Solid relationship: observed in implementation or reproduced behavior.
- Dashed relationship: inferred or documented but not verified.
- Question marker: important relationship or ownership remains unknown.

Cite paths, symbols, schemas, logs, or test scenarios below the diagram instead of crowding nodes with evidence.
