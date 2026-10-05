# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository state

Pre-implementation. The repo holds the game design and an agent-skills directory — no source code, no dependency manifest, no commits on `master`. There are no build, lint, test, or run commands to list yet, and the stack is an open decision rather than an unstated one: ask before assuming a language or engine. Record the commands here as soon as tooling lands.

## The design document

`docs/game-design-v0.1.0.md` is the single source of truth for the game. Read it before any design or implementation work, and change rules there rather than restating them in code comments or new docs.

**Its numbers are placeholders.** Every quantity lives in the design's *Tuning knobs* table and is a balance knob to be tuned through playtesting. Keep them as tunable data in one place, never as literals spread through the code.

## What the design forces on implementation

The design is settled; these are the consequences for whoever builds it, worth not re-deriving:

**Asymmetric visibility is the game, so the server owns it.** Employees see everything while the boss sees only their vision circle, and capture and fire prompts depend on who is in whose sight. That information gap *is* the gameplay, so an authoritative server must filter state per recipient before it leaves the process — a client that receives the full world and hides part of it in the UI is one devtools session away from having no game.

**Timed transitions are where cheating pays.** Room entry and the sit-down are deliberately not instant, and the race between them decides catches; capture prompts open and close on the same races. Arbitrate all of them on the server.

**Accrual is continuous.** Utility and work accrue from time spent in a state, not from discrete hourly events.

**Resolution order matters.** Fire versus sit-down, caught-while-holding-evidence, report races at lunch, and the bell each have an explicit order in the design; the individual rules alone do not determine outcomes, so implement the ordering explicitly.

**The roster shrinks mid-match.** Fired players become spectators, and the quota rescales with headcount, so eliminated players need a defined state from day one.

**The map is generated data, not a hand-built level.** v0.1.0 is 4 cabins in a square, but the design asks for a regular polygon of any size, so derive geometry from a cabin count instead of hard-coding four. Lunch is a separate level.

## Agent tooling in this repo

`.claude/skills/` holds general workflow skills — interviewing the user about a design, handoffs, teaching, questionnaires — not project tooling; `.claude/skills/README.md` indexes them and marks which are user-invoked only.

Two conventions:

- **Read `.claude/skills/writing-for-agents/SKILL.md` before editing this file, any `SKILL.md`, or any doc an agent reaches through a pointer.** It is the house style for agent-facing writing (context pointers, the information hierarchy, leading words, pruning), and `SKILL-MECHANICS.md` beside it covers frontmatter and invocation choice.
- Each skill targets both Claude Code and Codex: `SKILL.md` frontmatter plus a parallel `agents/openai.yaml`. Adding or changing a skill means both files, and the invocation flags mirror each other — `disable-model-invocation: true` pairs with `policy.allow_implicit_invocation: false`.
