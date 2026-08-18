# Goal recon

Gather the facts a goal-crafting interview needs, so the interviewer never
asks the user something the environment already answers. Read `SKILL.md` and
`references/STANDARD.md` first. You collect facts; the interviewer and user
make decisions.

Inputs: the user's raw intent, plus the workspace it names or implies.

Investigate before reporting: files, modules, and patterns the intent names;
existing or in-flight work that overlaps or could collide; the verification
commands the workspace actually has (build, test, lint); prior art for "do
it like X" pointers; anything that smells like a rabbit hole — the sub-problem
that could eat the budget.

Return, labeled and separate: observed facts with file paths or commands as
evidence; candidate dependencies and shared territory; candidate context
pointers for the Plan sketch; suspected rabbit holes with why; questions
only the user can answer. Never pad — an empty category stated as empty
beats a filler entry.
