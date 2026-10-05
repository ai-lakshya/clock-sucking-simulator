# Clock Sucking Simulator — Game Design, v0.1.0

**Status: final for v0.1.0.** Only the values in [Tuning knobs](#tuning-knobs) are expected to change through playtesting.

The complete design of the game for version 0.1.0. This document describes the game only — how it plays and why — and leaves implementation open.

Every number lives in [Tuning knobs](#tuning-knobs) and is a placeholder to be tuned for fun. The body refers to knobs by **name**, never by value.

## Pitch

Your company sucks the life out of you, so you suck the life out of the clock. A comedic, satirical, top-down 2D party game: four employees slack as hard as they dare across one six-day work week, while a boss prowls the corridor trying to catch them, and every co-worker is a potential snitch.

## Design pillars

- **The tension comes from people.** Working and slacking are a pure toggle with no minigames; all the drama comes from reading the boss, watching co-workers, and lying on voice chat.
- **Simple to grasp, no abilities.** Nobody has special powers or cooldowns. Asymmetry comes from what each side can *see* and how fast they move, and nothing else.
- **Greed against the group.** Each employee wants to slack more than everyone else, but slacking together is the only way the group beats the boss — and the laziest slacker of a failed day is the one who gets fired.
- **Fog of war favours the employees; the room favours the boss.** Employees see everything but can only act on what's near; the boss is half-blind in the corridor and all-powerful inside a cabin.

## Roles and identity

One player is the **boss**, chosen at random; the other four are **employees**. A match is one work week; afterwards the lobby can rematch with a freshly randomised boss.

Identity is **anonymous**. All avatars look identical apart from colour: everyone can see which avatar is the boss, but not which friend is playing it. Player names are revealed on the end screen.

Voice chat is **global and always open**, boss included. Voices are the leak: an employee who plans out loud may be overheard by the boss, and a boss who talks too much may be recognised. Working out who's who is part of the fun.

## Winning and losing

**The boss wins** the moment any of these is true, and the match ends immediately:

- **Days met** reaches the **days-met target** (a day is *met* when the team hits that day's quota).
- Every employee has been fired.

**The employees win**, as a group, if the week ends with none of the above. Among the surviving employees, the one with the highest **utility** is **Employee of the Week** — the real winner. Tied survivors share the title. A fired employee always loses, whatever their utility.

The shape this gives each day: the group wants the quota to fail, every individual wants to slack more than the others, and nobody wants to be the lowest worker on a failed day.

## The work week

A week is **week length** days. Each day runs:

1. **Morning** — work hours 1 to 4 on the office level.
2. **Lunch** — the lunch level (see [Lunch](#lunch)).
3. **Afternoon** — work hours 5 to 8 on the office level.
4. **The bell** — the end-of-day resolution.

The in-game clock runs faster than real time: each in-game hour passes in **hour length** of real time, a rate to be set in playtesting for the most fun. Scoring is **continuous**: utility and work accrue every moment according to your current state, so switching mid-hour is fine and hours are just the clock on screen.

At the start of each work period every employee spawns seated at their own desk, working.

### The bell

At the bell, play freezes instantly — whoever is mid-roam is saved by the bell. Then:

1. Every employee's work done today is revealed.
2. If the team met the quota, the day counts toward **days met**.
3. If the quota was missed, the boss has **firing decision time** to fire the day's **lowest worker** or spare them. Ties for lowest: the boss picks among the tied.

### The quota

The daily quota is a **team total** of work units, sized so that no single employee can carry the day alone — even working all eight hours. It scales with the number of employees still employed (**quota per employee**) and is recalculated from the day after a firing, never mid-day.

Everyone, boss included, sees a live **team progress bar** toward today's quota. It is the boss's one global signal: a bar crawling slowly says people are slacking, which pushes employees to stagger their slacking. Individual work totals stay hidden until the bell, so who's actually lowest is a guess — and a lie told at lunch.

## Employees

### States

An employee's state follows from where they are; there is no mode menu.

| State | Where | Earns per hour | Fireable? |
|---|---|---|---|
| **Working** | Seated at their own desk | **work utility** + **work units** | No |
| **Clock-sucking** | In their own cabin, not seated | **slack utility**, no work | Yes |
| **Roaming** (snitching) | Anywhere outside their own cabin | **slack utility**, no work | Yes |

Going *from* work is instant: stand up and you are slacking; walk out and you are roaming. Going *back* to work is the **sit-down**: inside your own cabin, a "get to work" prompt is always available; pressing it walks you to your desk and sits you down, and you count as slacking — catchable — until you are seated. A roaming employee must first walk back through one of their own cabin's gates. The sit-down is the gamble at the heart of the game: how close can the boss get before you start it?

### Snitching

Roaming *is* snitching: there is no target to select, walking into a co-worker's cabin is the choice. Because every employee can see every co-worker's state, a snitch trip is less about finding out and more about pressure — the target sees you coming and must decide whether to start their sit-down early or bait you in.

## Vision

| Who | Where | Sees | Can act on |
|---|---|---|---|
| Employee | Anywhere | The whole office, all the time: every avatar, every employee's state, the boss | Only what's in their vision circle |
| Boss | Anywhere | Only their vision circle | Only what's in their vision circle |

Every player has a **vision circle** centred on themselves. Its radius depends on where they stand: **cabin vision radius** inside a cabin, the smaller **corridor vision radius** in the corridor. The radius switches once a room entry completes or the player steps out. Walls block the circle and gates are openings. Being *in someone's sight* means being inside their vision circle, and every rule below that depends on sight uses it. Entering any room, for anyone, takes the **room-entry delay**.

The boss moves at **boss speed**, slightly faster than **employee speed**, so a roaming snitch can be run down — but every employee can see the boss coming.

## The boss

### Firing

While the boss can act on an employee who is slacking or roaming, a **fire button** for that employee appears. The boss must press it; nothing fires automatically. One button per employee: two slackers in a room means two presses, which may give the second one time to finish their sit-down. An employee seated and working when the boss tries is safe.

Being fired is permanent: the player becomes a [spectator](#fired-players).

### Strategies

The design supports two boss plans that pull against each other:

- **Enforcer** — keep pressure on everyone so the quota is met on enough days.
- **Hunter** — catch slackers and fire employees until none are left.

Firing shrinks the workforce, which shrinks the quota but also the people available to meet it. Camping one cabin wins neither way: one employee working can't meet the quota alone, and the other three slack freely.

## Evidence

**Evidence** is a single-use token naming one co-worker. An employee can hold any number of tokens, on different co-workers or several on the same one. A token vanishes when spent, or when either its holder or its target is fired.

### Capture

Evidence is gained by **capture**. A capture prompt appears and stays until pressed or until its condition ends:

- **Snitch captures slacker** — B is in A's sight while B is clock-sucking or mid-sit-down. A gets a capture prompt on B until A presses it, B is seated, or B leaves A's sight.
- **Worker captures snitch** — B is working while A is in B's sight. B gets a capture prompt on A until B presses it or A leaves B's sight.
- **Corridor captures** — two roaming employees in each other's sight can each capture the other.

So a snitch who arrives too late hands their target evidence instead. Baiting is legal and encouraged: keep slacking until the snitch is almost through the gate, then sit down.

Only the **victim** is told they were captured. Nobody else knows who holds evidence on whom, which keeps lunch politics open to bluffing.

### Reporting

Spending evidence is a **report**. One report spends **every token the reporter holds** at once, and the boss gets a fire button for each named target, usable from anywhere. The boss still chooses whether to press it. A report can be made:

- **During work hours** — when the boss is in your cabin and you are working.
- **At lunch** — during a visit to the boss's cabin.

A report is a real action and can't be faked. Anything can be *said* around it.

### Caught holding evidence

When the boss presses fire on an employee who holds evidence, that employee chooses:

- **Take it** — they are fired.
- **Snitch** — they report with every token they hold, survive, and **lose all their work done today**. That makes them very likely to be the lowest worker at the bell, where they can still be fired.

## Lunch

Lunch is its own level: a **cafeteria** and a **boss's cabin**, with full visibility of where everyone is. It runs for **lunch length** of real time. Nobody can be caught, nobody earns utility or work, and no captures happen.

At lunch time, everyone is teleported there; all pending capture and fire prompts are cancelled.

- The boss is locked in the boss's cabin for all of lunch.
- Employees hang out in the cafeteria — scheming, deceiving, accusing — or visit the boss.
- Visits are optional and one employee at a time. While someone's inside, the others see a **busy** sign and wait.
- Each visit is capped at **visit length**, but visits are unlimited in number, back-to-back included. When the cabin frees up, the first employee to press the **visit button** gets in — there is no queue.
- A visit needn't include a report. Any employee can visit just to **block** the cabin and run down the lunch clock: if A knows B holds evidence on them, A can get in first, stall until the cap, then win the button race again, and keep B out until lunch ends.
- Two employees holding evidence on each other are in a race: whoever reaches the boss first reports first, and the other's evidence dies with them.
- Fires from lunch reports take effect immediately.

## The office

Cabins ring a central corridor where the boss patrols. Each cabin has two gates, a desk, and belongs to one employee. The office is a regular polygon with one cabin per side; v0.1.0 has **4 cabins in a square**, one per employee.

When an employee is fired, their cabin stays open as part of the map. Entering it counts as roaming.

## Fired players

Fired players **spectate**: they watch the rest of the week and stay on voice chat, but have no in-game actions. They can still talk — so a fired player helping the boss, or taking revenge on whoever snitched them out, is part of the comedy.

## Tuning knobs

All values are starting guesses for playtesting.

| Knob | Starting value | Notes |
|---|---|---|
| Players | 4 employees + 1 boss | Fixed for v0.1.0 |
| Week length | 6 days | |
| Work hours per day | 8 (4 + lunch + 4) | |
| Hour length | 15 s | Real time per in-game hour; the clock runs faster than real time |
| Work utility | 1 per hour | |
| Work units | 1 per hour | |
| Slack utility | 5 per hour | Roaming earns the same |
| Quota per employee | ~60% of a full day's work | Team quota = this × employees still employed |
| Days-met target | Undecided | Boss wins when reached |
| Firing decision time | ~10 s | |
| Room-entry delay | 0.25 s | Everyone, every room |
| Sit-down time | Undecided | Must exceed the room-entry delay so slacking is a gamble |
| Boss speed | Slightly above employee speed | |
| Cabin vision radius | Undecided | Large; applies to anyone inside a cabin |
| Corridor vision radius | Undecided | Smaller than the cabin radius |
| Lunch length | 60–90 s real time | |
| Visit length | ~15 s | Per visit; the number of visits is uncapped |

## Open for later versions

- Scaling beyond 4 employees: more cabins and bigger polygons.
- Isometric view instead of top-down.
- Measuring the boss's work win in total hours worked rather than days met.
- Spectators interacting with the game (ghost mechanics).
- Series play with a running score across rematches.
- The "office game" that inspired this one alongside Among Us — its name is still unknown.
