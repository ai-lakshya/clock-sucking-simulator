# Prototype Technical Design Doc (Python + pygame-ce + uv)

Oct 6, 2026 · @Lakshya Bamne

## Overview

**Yes, this stack is platform independent, and you can develop on Windows and Linux independently.** Python, pygame-ce and uv all run natively on both. uv's lockfile makes both machines install exactly the same package versions. You commit on one machine, pull on the other, run one command, and you're playing.

**Goal:** in 4 weeks, build a playable top-down prototype of the asymmetric game. It must answer one question: *is the core idea fun?* Rectangles and circles only, no art.

**Hard requirements**

- **R1: Windows + Linux parity.** Every commit must run on both OSes with the same commands. Neither machine is "the main one". CI checks both on every push.
- **R2: Reproducible setup.** A fresh clone runs with `uv sync` then `uv run game`. There are no manual installs beyond uv and Git.
- **R3: Tunable without code.** All feel numbers (speeds, ranges, cooldowns, round length) live in JSON and reload while the game runs.
- **R4: Per-role views.** Each player only ever receives and draws what their role may see. This is the foundation for split-screen, LAN and the future C++ server.
- **R5: Deterministic simulation.** The game updates at a fixed 60 ticks per second with seeded randomness, so bugs and playtests can be replayed.

**Non-goals** (deliberately out of scope): internet play, in-game voice (use Discord), art and animation, menus beyond a start screen, saving, Steam, and macOS (it will likely work, but it isn't tested).

**Tech summary:** Python 3.12 · pygame-ce · pytmx + Tiled maps · JSON config · `socket` for LAN · pytest + Ruff · uv for Python versions, dependencies and running commands · GitHub Actions CI on Windows and Ubuntu · PyInstaller for builds.

## Day-1 setup

Do steps 1–6 once, on whichever machine you start on. Then do step 7 on the second machine. Total time: about one evening. Commands are from the [uv docs](https://docs.astral.sh/uv/getting-started/installation/) as of today.

### What uv is, and why it helps

uv is one tool that replaces `pip`, `venv` and `pyenv`. It installs the right Python version, creates the project's virtual environment (a private folder of packages, `.venv`), and records exact package versions in **`uv.lock`**. Because `uv.lock` is committed to Git, Windows and Linux get identical dependencies. `uv run <cmd>` always runs inside that environment, so you never need to "activate" anything.

### 1. Install the tools (each machine)

**Windows (PowerShell):**

```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
winget install --id Git.Git -e
```

**Linux:**

```
curl -LsSf https://astral.sh/uv/install.sh | sh
sudo apt install git   # or your distro's package manager
```

Open a new terminal and check that `uv --version` and `git --version` both work. Also install **VS Code** with the Python extension, and **Tiled** (map editor, [mapeditor.org](https://www.mapeditor.org)) on both machines.

### 2. Create the project (first machine only)

```
uv init asym-proto          # creates src/asym_proto/, pyproject.toml, .python-version, git repo
cd asym-proto
uv python pin 3.12          # both machines will use Python 3.12
uv add pygame-ce pytmx      # runtime dependencies
uv add --dev pytest ruff pyinstaller   # tools only you need
```

### 3. Make `pyproject.toml` look like this

The part to edit is `[project.scripts]`. It creates the `game` command.

```
[project]
name = "asym-proto"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["pygame-ce", "pytmx"]

[project.scripts]
game = "asym_proto.main:main"

[dependency-groups]
dev = ["pytest", "ruff", "pyinstaller"]

[build-system]
requires = ["uv_build>=0.12,<0.13"]
build-backend = "uv_build"

[tool.ruff]
line-length = 100
```

The exact version pins after `uv add` will differ; keep whatever uv writes.

### 4. Add the Git hygiene files

**`.gitattributes`** stores every text file with Linux line endings (LF), so diffs don't explode between OSes:

```
* text=auto eol=lf
*.png binary
*.wav binary
*.ogg binary
```

**`.gitignore`:**

```
.venv/
__pycache__/
build/
dist/
*.spec
.pytest_cache/
.ruff_cache/
playtest_logs/
```

Commit `uv.lock`, `.python-version` and `pyproject.toml`. Never commit `.venv`.

### 5. Write the smallest possible game

`src/asym_proto/main.py`:

```
import pygame

def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((1280, 720), pygame.SCALED | pygame.RESIZABLE)
    clock = pygame.time.Clock()
    pos = pygame.Vector2(640, 360)
    running = True
    while running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(keys[pygame.K_d] - keys[pygame.K_a], keys[pygame.K_s] - keys[pygame.K_w])
        if move.length_squared() > 0:
            pos += move.normalize() * 300 * dt
        screen.fill((20, 20, 28))
        pygame.draw.circle(screen, (230, 90, 80), pos, 16)
        pygame.display.flip()
    pygame.quit()
```

Run it with `uv run game`. A red dot moves with WASD. Then push the repo to GitHub.

### 6. Editor settings shared by both machines

Commit `.vscode/settings.json` so both editors behave the same:

```
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv",
  "files.eol": "\n",
  "editor.formatOnSave": true,
  "[python]": { "editor.defaultFormatter": "charliermarsh.ruff" }
}
```

### 7. Second machine

```
git clone <your repo url>
cd asym-proto
uv sync        # installs Python 3.12 + exact locked packages
uv run game
```

If the dot moves on both machines, R1 and R2 are satisfied. From now on, the daily loop on either machine is `git pull` → `uv sync` → `uv run game` → code → `uv run pytest` → commit → push.

## Cross-platform rules

Python hides most OS differences, but these ten traps are what actually break "works on my Windows, crashes on my Linux". Follow the rule column and R1 stays true.

| Trap | What goes wrong | Rule |
| --- | --- | --- |
| File paths | `"assets\maps\a.tmx"` fails on Linux | Always use `pathlib.Path`, built from one `ROOT` constant (see below). Never hard-code `\` or `/`. |
| Working directory | Game only finds assets when launched from a certain folder | Resolve every asset relative to the package, never to the current directory |
| Filename case | `Player.png` vs `player.png`: fine on Windows, missing on Linux | All asset files lowercase, `snake_case`, no spaces |
| Line endings | Every line shows as changed after switching machines | `.gitattributes` with `eol=lf` (Day-1 step 4) |
| Fonts | `SysFont("Arial")` doesn't exist on Linux | Ship one free `.ttf` in `assets/fonts/` and load it by path |
| Gamepads | Different button numbers per OS and driver | Use `pygame._sdl2.controller` (SDL's standard controller mapping), with a keyboard fallback |
| Window scaling | Tiny or blurry window on high-DPI screens | Draw to a fixed 1280×720 virtual resolution with `pygame.SCALED` |
| Timing | Game runs faster on the faster machine | Fixed timestep (Concepts part 1); never move by "per frame" amounts |
| Networking | Windows Firewall silently blocks the LAN server | Allow Python through the firewall on first run; use one fixed port (e.g. 47800) defined in config |
| Builds | PyInstaller can't build a Linux binary on Windows | Build each OS's executable on that OS, or let CI do it (section on CI) |

**The path helper** every module uses (`src/asym_proto/paths.py`):

```
from pathlib import Path
import sys

# Works both in development and inside a PyInstaller build
if getattr(sys, "frozen", False):
    ROOT = Path(sys._MEIPASS)
else:
    ROOT = Path(__file__).resolve().parents[2]   # project root

ASSETS = ROOT / "assets"
CONFIG = ROOT / "config"

def asset(*parts: str) -> Path:
    return ASSETS.joinpath(*parts)
```

Usage: `pygame.image.load(asset("sprites", "hunter.png"))`. On Linux and Windows the same line works.

**Rule of thumb:** switch machines at least once a week during the prototype, even for an hour. CI catches crashes. Switching machines catches feel differences: controllers, screen sizes, performance.

## Architecture

The prototype is split so that **the simulation never knows how it is shown or where its inputs come from**. Inputs become *commands*. The simulation turns commands into a new world state each tick. `build_view` cuts out what each player may see. The renderer draws only that view. Swapping split-screen for LAN only changes which wires carry commands and views. The same split becomes your C++ engine.

&#91;embedded content: prototype data flow · commands in, views out\]

In week 4 the arrows marked Command and View become a network link: the host PC runs everything up to `build_view`, and the client PC only runs devices, input mapper and renderer.

### Folder layout

```
asym-proto/
├── pyproject.toml  uv.lock  .python-version  .gitattributes  .gitignore
├── config/
│   ├── roles.json        # per-role stats: speed, vision, abilities, win condition
│   ├── tuning.json       # global numbers: tick rate, round length, friction
│   └── controls.json     # key and gamepad bindings per player slot
├── assets/
│   ├── maps/             # Tiled .tmx maps + tilesets
│   └── fonts/            # one bundled .ttf
├── src/asym_proto/
│   ├── main.py           # entry point: creates the app, runs the state machine
│   ├── paths.py          # ROOT / asset() helper (cross-platform)
│   ├── core/             # loop.py (fixed timestep), rng.py, config.py (load + hot reload)
│   ├── input/            # mapper.py (devices → actions), commands.py
│   ├── sim/              # NO drawing code here
│   │   ├── world.py      # World: entities, map, tick counter
│   │   ├── entities.py   # dataclass components
│   │   ├── systems/      # movement, collision, abilities, vision, rules
│   │   └── ai/           # bots.py (state machines), pathfind.py (BFS/A*)
│   ├── view/             # build_view.py, camera.py, renderer.py, hud.py, fog.py
│   ├── net/              # protocol.py, host.py, client.py (week 4)
│   ├── states/           # boot, lobby, match, results
│   └── debug/            # overlay.py: FPS, tick, entity inspector, toggles
├── tests/                # pytest: collision, vision, determinism, protocol
└── playtest_logs/        # notes per session (git-ignored or kept, your choice)
```

**Three dependency rules** keep this clean:

1. `sim/` may use `pygame.Vector2` and `pygame.Rect` (plain math), but never `pygame.display`, `draw` or `event`. Tests and the LAN host can then run it without a window.
2. `view/` reads the world only through `build_view`. It never changes the world.
3. `input/` produces commands only. It never moves entities directly.

## Concepts part 1: loop, movement, collision, camera

Each concept below covers what it is, why the prototype needs it, a minimal code shape, and the common trap. All of them transfer directly to the C++ engine.

### 1. The game loop

**What:** a game is one `while` loop that runs 60+ times per second. Every pass does three things in order: **read input → update the world → draw the frame**. Nothing happens "in the background". If something moves, it's because the update step moved it.

**Why it matters:** in pygame you write this loop yourself (Day-1 step 5). In C++ you will write the same loop on top of SDL3.

**Trap:** doing slow work (loading files, printing a lot) inside the loop causes stutter. Load everything before the loop starts.

### 2. Fixed timestep (the most important concept here)

**What:** frames take varying time (16 ms, then 21 ms, then 15 ms). If movement uses that varying time, the game behaves slightly differently on each machine and each run. A **fixed timestep** updates the simulation in equal steps of exactly 1/60 s, no matter how fast frames are drawn. An *accumulator* stores leftover time.

```
TICK = 1 / 60
accumulator = 0.0
while running:
    frame_time = min(clock.tick() / 1000, 0.25)   # cap: avoid "spiral of death" after a freeze
    accumulator += frame_time
    commands = input_mapper.poll()                 # read input once per frame
    while accumulator >= TICK:
        world.step(commands, TICK)                 # always the same step size
        accumulator -= TICK
    alpha = accumulator / TICK                     # 0..1: how far into the next tick we are
    renderer.draw(build_view(world, player), alpha)
```

**Why it matters:** it gives requirement R5 (determinism). The same commands give the same result on both your machines. It also makes networking possible later, because every machine counts the same numbered ticks. `alpha` lets the renderer blend between the previous and current position for smooth motion.

**Trap:** using `dt` from `clock.tick()` directly inside `world.step`. Always pass `TICK`.

### 3. Vectors and movement that feels good

**What:** a vector is an (x, y) pair. It can mean a position, a direction or a velocity. `pygame.Vector2` gives you `+`, `-`, `* scalar`, `.length()`, `.normalize()` and `.lerp()`.

**Feel = acceleration + friction.** Setting position directly feels robotic. Changing *velocity* toward a target feels alive:

```
def move(e, wish_dir: Vector2, stats, dt):
    target = wish_dir * stats.max_speed           # wish_dir is normalised or zero
    rate = stats.accel if wish_dir.length_squared() else stats.friction
    e.vel = e.vel.move_towards(target, rate * dt)  # pygame-ce Vector2 method
    e.pos += e.vel * dt
```

`max_speed`, `accel` and `friction` come from `roles.json`. Tuning these three numbers per role is half of "does it feel good?".

**Trap:** diagonal movement faster than straight movement. Normalise the input direction first.

### 4. Collision

**What:** detecting overlap (collision *detection*) and pushing objects apart (collision *resolution*). Top-down games need two shapes:

- **AABB** (axis-aligned bounding box): a rectangle that never rotates. It is perfect for walls and tiles. `pygame.Rect.colliderect` tests overlap.
- **Circle**: perfect for characters. Two circles overlap when the distance between centres is less than the sum of the radii.

**Resolution against tile walls, the reliable way:** move along X, fix overlaps, then move along Y, fix overlaps. Doing the axes separately makes characters slide smoothly along walls instead of sticking:

```
e.pos.x += e.vel.x * dt
for wall in walls_near(e):
    if overlaps(e, wall): push_out_x(e, wall); e.vel.x = 0
e.pos.y += e.vel.y * dt
for wall in walls_near(e):
    if overlaps(e, wall): push_out_y(e, wall); e.vel.y = 0
```

**`walls_near`:** don't test every wall. Convert the entity's position into tile coordinates (`int(x // TILE_SIZE)`) and check only the 3×3 tiles around it. This is the "spatial grid" idea you'll reuse in C++.

**Trap:** very fast objects passing through thin walls ("tunnelling"). Keep max speed below one tile per tick, or split fast moves into smaller steps.

### 5. Camera, world space and screen space

**What:** the world uses its own coordinates (a 3200×3200 map). The screen is 1280×720. The **camera** is an offset that converts between them: `screen = world - camera_pos + screen_center`.

**Smooth follow:** `camera_pos = camera_pos.lerp(target_pos, 0.15)` per frame gives a soft, cinematic follow.

**Split-screen:** each player gets their own camera and a **viewport**. A viewport is a sub-rectangle of the screen (`screen.subsurface(rect)`) that the renderer draws that player's view into.

**Trap:** mixing world and screen coordinates, such as mouse aiming. Convert the mouse position to world coordinates with the inverse formula before using it in the simulation.

## Concepts part 2: input, entities, state machines, data

### 6. Input mapping and commands

**What:** raw input ("W key down", "left stick at 0.7, -0.2") is turned into **actions** ("move up", "use ability"). Once per tick, actions are packed into a small **command** object per player.

```
@dataclass(frozen=True)
class Command:
    tick: int
    move: tuple[float, float]   # -1..1 on each axis
    ability: bool
    interact: bool
```

**Why it matters:** the simulation only ever sees `Command`s. A bot, a keyboard, a gamepad and a network packet all produce the same thing. Split-screen is just two players with different bindings from `controls.json`. LAN is commands arriving over a socket. Recording commands also gives you **replays** for free.

**Gamepads:** use `pygame._sdl2.controller` so an Xbox, PlayStation or generic pad reports the same buttons on Windows and Linux. Apply a **dead zone** (ignore stick values below \~0.2), because sticks never rest exactly at zero.

**Trap:** reading `pygame.key.get_pressed()` inside game systems. Only `input/` touches devices.

### 7. Entities and components ("ECS-lite")

**What:** everything in the world (players, generators, doors, projectiles) is an **entity**: an ID plus some **components**, which are plain data. **Systems** are functions that loop over entities having certain components. Behaviour comes from *which data an entity has*, not from a deep class hierarchy.

In Python, keep it simple: one dataclass per component, and a dictionary per component type.

```
@dataclass
class Body:   pos: Vector2; vel: Vector2; radius: float
@dataclass
class Vision: range: float; cone_deg: float   # 360 = all around
@dataclass
class Role:   name: str; team: str

class World:
    def __init__(self):
        self.next_id = 0
        self.bodies: dict[int, Body] = {}
        self.visions: dict[int, Vision] = {}
        self.roles: dict[int, Role] = {}

def movement_system(world, commands, dt):
    for eid, body in world.bodies.items():
        ...
```

**Why it matters:** adding a new role or object becomes "attach different components", which is your "scale later" plan. This is exactly the ECS you'll write properly in C++. Python dictionaries are the slow but simple version of C++ arrays.

**Trap:** putting rendering data (colours, sprites) into simulation components. Keep a separate `Look` component that only `view/` reads.

### 8. State machines

**What:** a state machine is a value saying "what mode am I in", plus rules for when to switch. You'll use two kinds:

- **Game states:** `Boot → Lobby → Match → Results → Lobby`. Each state is a class with `enter()`, `handle(commands)`, `update(dt)`, `draw()` and `exit()`. `main.py` holds the current state and swaps it.
- **Entity and bot states:** a survivor bot is `Wander → Repair → Flee → Hide`, and a hunter bot is `Patrol → Chase → Search`. Each state checks its exit conditions every tick ("enemy visible → Chase").

```
class HunterBot:
    def think(self, me, view) -> Command:
        match self.state:
            case "patrol": ...; if view.visible_enemies: self.state = "chase"
            case "chase":  ...; if not view.visible_enemies: self.state = "search"
            case "search": ...
```

**Why it matters:** it keeps "what happens when" readable. Bots built this way are good enough to playtest each role alone.

**Trap:** bots reading the whole world. Give bots the same `build_view` a human gets, so they can't cheat and your fog of war gets tested for free.

### 9. Data-driven config and hot reload

**What:** numbers that affect feel live in JSON, not code:

```
{
  "hunter":   { "max_speed": 260, "accel": 1800, "friction": 2200, "vision_range": 420, "cone_deg": 70,  "radius": 18 },
  "survivor": { "max_speed": 230, "accel": 2000, "friction": 2600, "vision_range": 260, "cone_deg": 360, "radius": 14 }
}
```

These values are placeholders to start tuning from.

**Hot reload:** press F5 (or check file modification times every second) to reload `config/*.json` into the running game. Change a number, save, and feel the difference immediately without restarting. Expect this to be the single biggest speed-up in prototyping.

**Determinism helpers (R5):** one `random.Random(seed)` instance lives in the world. Never use the global `random` module in `sim/`. Log the seed at the start of each match, so a weird round can be replayed.

**Debug overlay:** a toggle key (F1) draws the tick number, FPS, entity count, each entity's state and the vision cones. Add it in week 1, because every later bug is easier with it on.

## Concepts part 3: vision, views, bots, LAN

### 10. Vision and line of sight

**What:** decide whether entity A can see entity B. That takes three checks, from cheapest to most expensive:

1. **Range:** is the distance less than A's `vision_range`? Compare squared distances to skip the square root.
2. **Cone:** is B inside A's field of view? Take the angle between A's facing direction and the direction to B (`facing.angle_to(to_b)`). It must be within `cone_deg / 2`.
3. **Line of sight:** does any wall tile block the straight line from A to B? Step along the line through the tile grid. Use a grid traversal such as **DDA**, or simply sample every half-tile. If any sampled tile is a wall, B is hidden.

```
def can_see(a, b, grid) -> bool:
    to_b = b.pos - a.pos
    if to_b.length_squared() > a.vision_range ** 2: return False
    if abs(a.facing.angle_to(to_b)) > a.cone_deg / 2: return False   # normalise angle to -180..180 first
    return grid.line_clear(a.pos, b.pos)
```

**Fog of war (drawing):** cast \~120 rays in a fan from the player, each stopping at the first wall. The ray end points form a **visibility polygon**. Draw a dark overlay over the whole viewport, then cut that polygon out of it (draw it with a transparent colour onto the overlay surface). Everything outside is shadow. [Red Blob Games' 2D visibility article](https://www.redblobgames.com/articles/visibility/) explains the full version.

**Trap:** doing per-pixel work in Python. Rays and polygons are fast enough. Pixel loops are not.

### 11. Per-role views (R4)

**What:** a **view** is a plain data snapshot of what one player is allowed to know right now: their own entity, visible entities, the map, objective states, their cooldowns and the remaining time.

```
@dataclass
class View:
    tick: int
    me: EntitySnapshot
    visible: list[EntitySnapshot]     # filtered by can_see()
    objectives: list[ObjectiveState]
    time_left: float

def build_view(world, player_id) -> View: ...
```

**Why it matters:** the renderer, the bots and the network client all consume `View`s. Hidden information is enforced in one function, in the simulation, not in drawing code. When LAN arrives, you send the `View` over the wire, so the other player's PC *never receives* hidden positions. This is the prototype of the interest management in your C++ roadmap.

### 12. Bots and pathfinding

**What:** bots need to get from A to B around walls. On a tile grid:

- **BFS (breadth-first search):** explores tiles outward like a ripple until it reaches the target. It always finds a shortest path on a uniform grid. It is simple and enough for the prototype.
- **A\*:** BFS plus a "which tile looks closer to the goal" priority (a *heuristic*, e.g. Manhattan distance). It explores far fewer tiles. Upgrade to it if BFS gets slow.

Recompute paths a few times per second, not every tick. Bots follow the path by steering toward the next tile centre, producing the same `Command`s a human would.

**Read:** [Red Blob Games: Introduction to A\*](https://www.redblobgames.com/pathfinding/a-star/introduction.html), the clearest explanation that exists.

### 13. LAN networking (week 4)

**Model:** one PC is the **host**. It runs the only real `World`. The other PC is a **client** that runs no simulation at all:

- Each tick, the client sends its `Command` to the host.
- The host applies all commands, steps the world, and sends each client its own `View`.
- The client just draws the latest `View`.

On a home network the delay is a few milliseconds, so no prediction is needed. (Prediction is a C++ month-4 topic.)

**TCP vs UDP:** TCP guarantees delivery and order but can stall when a packet is lost. UDP is fast but packets may be lost or reordered. Real action games use UDP. For a LAN prototype, **TCP is fine and much simpler**: use it now, and learn UDP properly in C++ with ENet.

**Framing:** TCP is a stream of bytes, not messages. One `send` may arrive as two `recv`s, or two sends as one. The simplest fix is **one JSON object per line**. Read into a buffer, split on `\n`, and parse each complete line.

```
# shared message shape (net/protocol.py)
{"type": "cmd",  "tick": 812, "move": [0, -1], "ability": false}
{"type": "view", "tick": 812, "me": {...}, "visible": [...], "time_left": 143.2}
```

**Don't block the game loop:** call `sock.setblocking(False)` and read whatever has arrived once per frame, or run the socket in a background `threading.Thread` that pushes messages into a `queue.Queue`. Either works on both OSes.

**Cross-platform notes:** bind the host to `0.0.0.0` and a fixed port from `tuning.json`. Allow Python through Windows Firewall the first time. Find the host's local IP with `ip a` (Linux) or `ipconfig` (Windows), and type it in the client's lobby screen.

**Trap:** sending the whole `World`. Always send the filtered `View`, or the client can see everything.

## 4-week build plan

The plan reaches something playable on day 2 and puts real players in front of it in week 3. Run it alongside about 30% time on C++ Foundations. If a gate slips, cut features, not playtests.

&#91;embedded content: 4-week prototype plan · one gate per week\]

The week-4 verdict is a one-page note: the checklist from *What the prototype must prove* (in the stack decision doc), what changed during playtests, and the final JSON numbers. That note, the maps and the JSON are what carry into the C++ build.

## Testing, CI and builds

### Tests worth writing (pytest)

Skip testing drawing code. Test the parts that break silently:

- **Collision:** an entity pushed into a wall ends up touching it, never inside it.
- **Vision:** `can_see` is false through a wall and true in the open; the cone edges behave.
- **Determinism:** run 600 ticks twice with the same seed and the same recorded commands. Both final worlds must be identical. This guards R5 on both OSes.
- **Protocol:** a `Command` and a `View` survive JSON encode → decode unchanged; split lines are reassembled.

Run them with `uv run pytest`. Run `uv run ruff check .` and `uv run ruff format .` for lint and formatting.

### Headless smoke test

Add a `--smoke N` flag to `main()`: start a match with bots on both sides, run N ticks, exit with code 0. In CI there is no screen, so set `SDL_VIDEODRIVER=dummy` and `SDL_AUDIODRIVER=dummy`. pygame then runs without a window, and crashes in real game code are still caught.

### CI on Windows and Linux (`.github/workflows/ci.yml`)

This enforces R1 on every push. Action versions are from the [uv GitHub Actions guide](https://docs.astral.sh/uv/guides/integration/github/) as of today.

```
name: ci
on: [push, pull_request]
jobs:
  test:
    strategy:
      matrix:
        os: [windows-latest, ubuntu-latest]
    runs-on: ${{ matrix.os }}
    env:
      SDL_VIDEODRIVER: dummy
      SDL_AUDIODRIVER: dummy
    steps:
      - uses: actions/checkout@v7
      - uses: astral-sh/setup-uv@v9
        with:
          enable-cache: true
      - run: uv sync --locked --dev
      - run: uv run ruff check .
      - run: uv run pytest
      - run: uv run game --smoke 600
```

`--locked` makes CI fail if `uv.lock` is out of date, which catches a forgotten lockfile commit.

### Builds for playtesters (PyInstaller)

Add a two-line launcher at the project root, `run_game.py`:

```
from asym_proto.main import main
main()
```

Then build on each OS:

```
uv run pyinstaller run_game.py --name asym-proto --windowed --add-data "assets:assets" --add-data "config:config"
```

The result is `dist/asym-proto/` (a folder with the executable). Zip it and send it. PyInstaller can't cross-compile, so the Windows build comes from Windows and the Linux build from Linux. Later, add a CI job that runs this on both runners and uploads the zips with `actions/upload-artifact`.

Note that `paths.py` already handles the frozen case (`sys._MEIPASS`), so assets are found inside the build. Shipping `config/` inside the build means testers can edit the JSON too, which is useful for balance experiments.

### Playtest log

After every session, write a short markdown note in `playtest_logs/YYYY-MM-DD.md`:

- Who played which role, and the match seeds.
- Who won and the round lengths.
- One thing that felt great, and one thing that felt bad.
- What you changed in the JSON afterwards.

These notes, not the Python code, are the most valuable output of the prototype for the C++ build.

## Learning resources

- [uv documentation](https://docs.astral.sh/uv/): projects, `uv add`, `uv sync`, `uv run`, GitHub Actions.
- [pygame-ce documentation](https://pyga.me/docs/): `Vector2`, `Rect`, `Surface`, `display`, `_sdl2.controller`.
- [Game Programming Patterns](https://gameprogrammingpatterns.com): Game Loop, Update Method, Component, State and Command chapters, all used directly here.
- [Gaffer on Games: Fix Your Timestep](https://gafferongames.com/post/fix_your_timestep/): the fixed-timestep article. Read it in week 1.
- [Red Blob Games](https://www.redblobgames.com): grids, A\*, 2D visibility. Read in weeks 2–3.
- [Python `socket` HOWTO](https://docs.python.org/3/howto/sockets.html): read before week 4.
- [Tiled documentation](https://doc.mapeditor.org) and [pytmx on GitHub](https://github.com/bitcraft/pytmx): maps, layers and object layers for spawns and objectives.
- [PyInstaller manual](https://pyinstaller.org): `--add-data`, `--windowed`, one-folder builds.
