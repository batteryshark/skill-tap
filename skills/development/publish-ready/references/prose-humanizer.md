# Prose humanizer

Rewrite docs and comments so they read like a sharp engineer wrote them for a
peer whose time they respect — not like generated filler. The reader is scanning
for signal; every word that isn't signal reads as noise, and enough noise reads as
"nobody actually edited this."

The test for any sentence: **would a senior engineer who respects the reader keep
it?** If it hedges, hypes, or restates, cut it.

## The tells (why text reads as machine-generated)

- **Hedging and throat-clearing.** "It's worth noting that", "essentially",
  "basically", "simply", "just", "of course", "as we can see", "in order to".
  Delete them; the sentence is stronger without.
- **Marketing adjectives with no content.** "powerful", "robust",
  "comprehensive", "seamless", "flexible", "elegant", "rich", "intuitive",
  "cutting-edge", "state-of-the-art", "blazingly fast". These *claim* quality
  instead of *showing* it. Replace with a concrete fact or delete.
- **Thesaurus verbs.** "leverage" (use), "utilize" (use), "delve into" (cover),
  "unlock" (enable), "elevate" (improve), "harness", "facilitate", "employ".
- **Restating the obvious.** A heading followed by a sentence that repeats the
  heading. "In other words" after something already clear. Summary sections that
  re-list what's above. Say it once.
- **Fake symmetry / list-brain.** Everything forced into a bulleted list, or
  three parallel clauses where one point exists ("fast, reliable, and scalable").
  Real writing varies; use prose when it flows better than bullets.
- **Bold and emoji sprinkled for emphasis.** Bold on every other phrase stops
  meaning anything. Emoji in headings/READMEs read as decoration, not
  documentation. Cut both to near-zero.
- **Grandiose framing.** "In today's fast-paced world", "In the realm of", "When
  it comes to X", "At its core". Start with the actual thing.
- **Conversational residue.** "Certainly!", "Great question", "Let's dive in",
  "Happy coding!", "I hope this helps". This is chat, not documentation.
- **Hollow transitions.** "Furthermore", "Moreover", "Additionally", "That being
  said" stacked as connective tissue between points that don't need them.

## Word/phrase swaps

| Instead of | Write |
|---|---|
| leverage / utilize / employ | use |
| in order to | to |
| a wide variety of / a plethora of / myriad | (name them, or "many") |
| is able to / has the ability to | can |
| due to the fact that | because |
| at this point in time | now |
| it's worth noting that X | X |
| this powerful tool allows you to | (just say what it does) |
| seamlessly integrates with | works with |
| robust / comprehensive solution | (say what it actually does) |
| in the event that | if |
| a number of | (the number, or "several") |

## Structural rules

- **Sentences over adjectives.** "Parses 10k-line files in under a second" beats
  "blazingly fast". Show the fact; let the reader conclude the adjective.
- **Active voice, concrete subjects.** "The scanner reads the manifest", not "The
  manifest is read by the system as part of the process."
- **One strong claim beats three weak ones.** Cut the qualifiers and the hedges
  around a claim, or cut the claim.
- **Bullets earn their bullet.** A list of parallel items is a list. A paragraph
  of connected reasoning is a paragraph. Don't bullet prose.
- **Bold is a spotlight.** If everything is bold, nothing is. Reserve it for the
  rare word the reader must not miss.
- **Headings are signposts, not restatements.** A section titled "Configuration"
  should not open with "This section covers configuration."

## README-specific

- First sentence answers "what is this and who is it for?" — no "Introduction"
  heading, no history, no throat-clearing.
- Then: why it exists (the problem), a quickstart that runs verbatim, and a short
  map of where things live.
- Cut the autobiography ("I built this because I was frustrated with…") unless it
  earns its place in one line.
- Version badges, "Table of Contents" for a two-screen README, and "Contributing"
  boilerplate nobody will follow are cost, not value — include only if real.

## Comments and docstrings

- **Explain why, not what.** `# increment i` is noise; the code says that.
  `# retry once — the API 500s on cold start` is signal.
- **Delete docstrings that restate the signature.** `"""Get the user."""` on
  `get_user()` adds nothing. Either say something useful (what it raises, what's
  surprising) or delete it.
- **No commented-out code.** History remembers it. A graveyard of `# old_thing()`
  lines reads as unfinished.
- **No dated apologies.** `# TODO: this is hacky, fix later`, `# not sure why this
  works` — either fix it, explain the real constraint, or delete the comment. An
  apology in a comment invites the reader to distrust the code.

## Before / after

**Before:**
> This powerful and flexible utility leverages a robust caching layer to
> seamlessly deliver blazingly fast lookups, making it an essential tool for any
> modern data pipeline.

**After:**
> Caches lookups in memory, so repeated queries don't hit the database.

---

**Before:**
> ## Overview
> This section provides a comprehensive overview of the configuration options
> that are available to the user. It's worth noting that there are a number of
> different settings that can be utilized in order to customize the behavior.

**After:**
> ## Configuration
> Settings live in `config.toml`. The three you'll actually change:

---

**Before:**
> 🚀 **Getting Started** 🚀
> Getting started is super easy! Simply just run the following command and you'll
> be up and running in no time:

**After:**
> ## Quickstart
> ```
> npm install && npm start
> ```

The rewrite is almost always shorter. If your edit added words, look again.
