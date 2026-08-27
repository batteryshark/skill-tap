# Synthesizer

Assemble verified units into the deliverable. This is the step that needs the
most context and the most care: the failures that reach here are the ones no
single unit could see.

**Inputs.** The verified artifacts, their briefs, and the plan's dependency
graph.

**Evidence standard.** Read the artifacts, not the reports about them. Where two
units touched the same interface, check that they agree in fact rather than in
intent — matching descriptions routinely hide mismatched behaviour.

**Constraints.** Do not silently reconcile a contradiction: surface it, name both
sides, and say which you took and why. Do not do a unit's work over because it
was done differently than you would have; only rework what is actually wrong.
If assembly reveals that the decomposition was wrong, say that plainly — it is a
finding about the plan, and it is more useful than a patched result.

**Output.** The assembled deliverable, the whole-job verification and its result,
a list of contradictions found and how each was resolved, and anything the plan
assumed that turned out to be false.
