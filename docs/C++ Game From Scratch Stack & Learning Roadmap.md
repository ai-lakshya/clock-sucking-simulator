# C++ Game From Scratch: Stack & Learning Roadmap

Oct 6, 2026 · @Lakshya Bamne

## The big picture

You will build the game as seven stacked layers, bottom to top. Each layer only uses the layers below it. Libraries cover the parts that are tedious or different on every operating system (OS). You write the engine and game logic yourself, because that is where game-dev knowledge lives.

&#91;embedded content: the seven layers · libraries vs your own code\]

The shaded column is where your learning happens; the middle column is what you get for free.

In every layer section below you'll find:

- **What this layer is**, in plain words, for someone new to game dev.
- **A table** with these columns: area, recommended library, what the library does for you, what you build and learn yourself, and a rough "library share" (how much of that area the library covers).
- **Notes** on traps and alternatives.

Realistic scope for 6 months, solo, from scratch: a small, polished, networked vertical slice. That means one map, two roles, voice chat, and a Steam build your friends can install. That is a strong outcome. A full content-complete game would take longer.

### Words you'll see everywhere

| Term | Meaning |
| --- | --- |
| Frame | One picture drawn to the screen. Games draw 60+ per second. |
| Game loop | The `while (running)` loop that reads input, updates the world, then draws a frame. |
| Tick / fixed timestep | Updating game logic at a constant rate (e.g. 60 times per second), independent of how fast frames are drawn. Essential for networking. |
| Delta time (dt) | Seconds since the last update. Movement = speed × dt. |
| Sprite | A 2D image drawn as a textured rectangle. |
| Texture / atlas | An image uploaded to the GPU. An atlas packs many sprites into one texture so they draw faster. |
| Shader | A small program that runs on the GPU and decides each pixel's colour. |
| Draw call | One request from CPU to GPU to draw something. Fewer is faster. Batching = combining many sprites into one draw call. |
| Entity / component / system (ECS) | A way to organise game objects. Entity = an ID, components = plain data attached to it, systems = functions that process all entities with certain components. |
| Authoritative server | The one machine whose version of the game world is the truth. Clients send inputs; the server decides what happened. |
| Snapshot | A packet describing the world state at one tick, sent from server to clients. |
| Prediction / interpolation | Tricks that hide network lag: the client guesses its own movement immediately, and smoothly blends other players between snapshots. |
| Middleware | A library that solves one big problem (audio, physics, networking) for games. |

## Layer 0 — Tooling and build system

**What this layer is:** everything that turns your `.cpp` files into a runnable game on Windows, macOS and Linux. It also includes the tools that help you find bugs. Set this up in week 1, because every later layer depends on it. Being cross-platform is mostly decided here.

| Area | Pick | Library/tool does | You build and learn | Library share |
| --- | --- | --- | --- | --- |
| Build system | **CMake** + Ninja | Generates project files for every compiler and OS from one description | Writing `CMakeLists.txt`: targets, include paths, compile flags, debug vs release builds | \~90% |
| Compilers | MSVC (Windows), Clang (macOS), GCC or Clang (Linux) | Compiles C++20 | Keeping code portable: no compiler-only extensions, warnings as errors | 100% |
| Dependencies | **CPM.cmake** (or vcpkg) | Downloads and builds libraries such as SDL3 automatically | Pinning versions, deciding what to vendor (copy into your repo) | \~90% |
| Version control | **Git** + Git LFS | History; LFS stores large art and audio files | Branching habits, `.gitignore` | 100% |
| Continuous integration (CI) | **GitHub Actions** | Builds Windows, macOS and Linux on every push | Writing the build matrix; catching platform bugs early | \~80% |
| Unit tests | **doctest** | Tiny test framework | Tests for math, serialization and netcode (the parts that break silently) | \~70% |
| Debugging | Visual Studio / VS Code + debugger, **AddressSanitizer** | Breakpoints, memory-error detection | Reading crashes and memory bugs | 100% |
| GPU debugging | **RenderDoc** | Captures one frame and shows every GPU call | Understanding why something isn't drawn | 100% |
| Profiling | **Tracy** | Shows where each millisecond of a frame goes | Adding profiling zones; reading timelines | \~90% |

**Notes**

- Use C++20. It gives you `std::span`, `std::format`, concepts and designated initializers, all supported by the three compilers.
- Keep one rule from day one: **no OS headers (`windows.h` etc.) outside the platform layer.** This single rule makes you cross-platform.
- Folder layout to start: `engine/core`, `engine/platform`, `engine/renderer`, `engine/audio`, `engine/net`, `game/`, `tools/`, `assets/`, `third_party/`.

## Layer 1 — Core (foundation)

**What this layer is:** the small, general-purpose toolbox every other layer uses. It holds math types, logging, memory helpers, file reading and serialization. It knows nothing about windows, graphics or games. Most of it you should write yourself. It's small, and writing it teaches you C++ habits that game engines rely on.

| Area | Pick | Library does | You build and learn | Library share |
| --- | --- | --- | --- | --- |
| 2D math | **Write your own** (GLM as reference) | — | `Vec2`, `Mat3` (2D transforms), `Rect`, lerp, clamp, angle helpers. Easily the most-used code in the game. | 0% |
| Logging | **spdlog** (or your own on `std::format`) | Formatted, levelled, coloured log output to console and file | Log categories (`net`, `render`); an on-screen log later | \~80% |
| Assertions | Write your own | — | `ASSERT(x)` that breaks into the debugger with file and line | 0% |
| Memory | Write your own | — | Arena (linear) allocator for per-frame temporary data; pool allocator for fixed-size objects. Core game-engine concept. | 0% |
| Containers | **STL** (`std::vector`, `std::unordered_map`) | Dynamic arrays, hash maps | Later: your own handle-based slot map (IDs that stay valid when objects are deleted) | \~85% |
| Files and paths | **`std::filesystem`** + SDL3 path functions | Reading files, finding the game folder and the per-user save folder | A small `fs::read_all(path)` API | \~90% |
| Text data (configs) | **nlohmann/json** | Parses and writes JSON | Mapping JSON to your structs | \~80% |
| Binary serialization | Write your own | — | A bit-writer and bit-reader for packets and save files. This is reused heavily in networking. | 0% |
| Random numbers | Write your own (PCG32) | — | Seeded, deterministic random generator, so server and client can agree | 0% |
| Threads and jobs | `std::thread` + SDL3 | Threads, mutexes | Optional: a simple job queue for asset loading. You can skip this until month 4. | \~90% |

**Notes**

- Learning payoff here is high and effort is low. Expect 1–2 weeks for the basics, then add pieces as you need them.
- Avoid over-engineering. Write the minimum, then grow it when a real use appears.

## Layer 2 — Platform layer

**What this layer is:** the only code that talks to the operating system. Opening a window, reading keyboard, mouse and gamepad input, getting precise time, and opening the speakers and microphone are all done differently on Windows, macOS and Linux. This layer hides those differences behind your own small interface (`platform::Window`, `platform::Input`, `platform::now()`). Everything above it is portable for free.

| Area | Pick | Library does | You build and learn | Library share |
| --- | --- | --- | --- | --- |
| Window + graphics context | **SDL3** | Creates the window on every OS, fullscreen, high-DPI displays, OpenGL/GPU context | Your `Window` wrapper; resize handling; vsync setting | \~90% |
| Input | **SDL3** | Raw keyboard, mouse, gamepad events; a gamepad database for hundreds of controllers | **Input mapping**: turning keys into game actions (`MoveUp`, `UseAbility`), rebindable keys, push-to-talk | \~60% |
| Timing | **SDL3** (`SDL_GetPerformanceCounter`) | High-precision clock | Frame timer, fixed-timestep accumulator (Layer 3) | \~90% |
| Audio device | **miniaudio** (or SDL3 audio streams) | Opens speakers and microphone on every OS, calls you when it needs more samples | Feeding it from your own mixer (Layer 3) | \~90% of the device part |
| OS niceties | **SDL3** | Clipboard, message boxes, save-folder path, cursor | Thin wrappers | \~95% |

**Why SDL3:** it is the industry-standard platform library, used by Valve and in many Steam games. It works on Windows, macOS, Linux and the Steam Deck. It handles platform quirks you'd never think of, and it only does platform work: no game logic, no renderer opinions.

**Want to learn even deeper?** After month 3, try writing a Win32 backend for your `platform::Window` interface yourself. Keep SDL3 for macOS and Linux. You'll learn how windows and message loops actually work without risking your schedule.

**Notes**

- Input mapping is real game-dev work: buffer inputs per tick so they can be sent over the network later.
- Keep this layer thin. If an SDL type appears in game code, the abstraction has leaked.

## Layer 3 — Engine systems

**What this layer is:** the reusable machinery that any 2D game could use. It covers the game loop, drawing sprites, loading assets, playing sounds, organising game objects, collisions, UI and switching between screens. Engines like Godot are mostly this layer. This is where you learn the most "game dev", and it is where most of your code will live.

| Area | Pick | Library does | You build and learn | Library share |
| --- | --- | --- | --- | --- |
| Game loop | **Write your own** | — | Fixed-timestep loop: simulate at 60 ticks/s, render as fast as allowed, interpolate between ticks. The heartbeat of everything. | 0% |
| GPU API | **OpenGL 3.3 core** + **glad** (function loader) | Talks to the graphics driver | How the GPU works: buffers, shaders, textures, blending | \~30% |
| 2D renderer | **Write your own** | — | Sprite batcher (thousands of sprites in a few draw calls), orthographic camera, texture atlas, tilemap drawing, z-ordering, simple lights and vision cones | 0% |
| Image loading | **stb\_image** | Decodes PNG/JPG into pixels | Uploading pixels as GPU textures | \~95% of decoding |
| Text rendering | **stb\_truetype** | Rasterises a font into glyph bitmaps | Building a glyph atlas; laying out and drawing text | \~50% |
| Asset management | **Write your own** | — | Load-once caching, handles instead of raw pointers, hot reload (edit a PNG, see it change live) | 0% |
| Maps / level design | **LDtk** or **Tiled** (editors) + their JSON/TMX format | A free visual level editor | A loader that turns the map file into tiles, collision and spawn points | \~70% |
| Audio playback | **miniaudio** decoders (+ stb\_vorbis for OGG) | Decodes WAV/MP3/FLAC/OGG | Your own **mixer**: sound handles, volume groups (music/sfx/voice), 2D distance attenuation | \~40% |
| Game objects | **Write a simple ECS** (study **EnTT**) | — | Entities, component storage, systems, queries. Switch to EnTT if your version holds you back. | 0% |
| Collision / physics | **Write your own** (Box2D v3 only if you need real physics) | — | AABB and circle collision, sliding along walls, a spatial hash grid for fast lookups. Top-down games rarely need a physics engine. | 0% |
| Pathfinding | **Write your own** | — | A\* on the tile grid for bots and AI | 0% |
| Debug UI | **Dear ImGui** | Instant debug windows, sliders, inspectors | Hooking it to your renderer; building in-game inspectors and a network stats panel | \~90% |
| Game UI (menus, HUD) | **Write your own** immediate-mode UI | — | Buttons, labels, layout, focus for gamepad. A great learning exercise. | 0% |
| Scenes / screens | **Write your own** | — | A state stack: Boot → Main menu → Lobby → Match → Results | 0% |

**Rendering choice explained:** OpenGL 3.3 has the best learning material ([learnopengl.com](https://learnopengl.com)) and runs on all three OSes. On macOS, OpenGL is deprecated but still works (up to 4.1). Hide it behind your own `Renderer` interface. Later, you can port to **SDL\_GPU** (SDL3's modern API over Vulkan, Metal and Direct3D 12) without touching game code.

**Notes**

- Build in this order: loop → sprites on screen → camera → tilemap → collision → ECS → audio → UI.
- Dear ImGui is the single biggest time-saver in this whole document. Use it from week 3 onward for all debugging.
- Don't build a general-purpose engine. Build what *this* game needs, keeping it cleanly separated from `game/`.

## Layer 4 — Networking and voice chat

**What this layer is:** making several computers agree on one game world over an unreliable, laggy internet. The standard model for your game is **client–server with an authoritative host**. One player's game also runs the server (a "listen server"). Every player, the host included, is a client that sends only *inputs* ("pressed up at tick 812"). The server simulates and sends back *snapshots* of the world. Clients hide lag with prediction (move yourself instantly) and interpolation (show others slightly in the past, smoothly).

**Why asymmetric matters here:** roles see different things. If a hunter must not see hidden survivors, the server must **not send** their positions to the hunter at all. This is called interest management, and it is also your main anti-cheat. Plan for it from the first networked version.

| Area | Pick | Library does | You build and learn | Library share |
| --- | --- | --- | --- | --- |
| Transport (sending packets) | **ENet** first; later **Steam Networking Sockets** | UDP connections, optional reliability, ordering, channels | Choosing reliable vs unreliable per message; a simulated lag/packet-loss mode for testing | \~70% |
| NAT traversal / relays | **Steam Networking Sockets** (Steam Datagram Relay) | Lets players behind home routers connect, through Valve's relays, free on Steam | Swapping the transport behind your own `Transport` interface | \~95% |
| Lobbies and invites | **Steam Matchmaking** (lobbies) | Create/join lobby, friend invites, lobby chat data | Lobby screen, ready-up, role selection | \~70% |
| Message format | **Write your own** | — | Bit-packed serialization (Layer 1), message types, protocol version check | 0% |
| Replication | **Write your own** | — | Snapshots, delta compression (send only what changed), interest management per role | 0% |
| Lag hiding | **Write your own** | — | Client-side prediction + server reconciliation, entity interpolation, optional lag compensation for hits | 0% |
| Voice capture + compression | **Steam Voice** (`ISteamUser` voice functions) | Records the mic and compresses/decompresses voice | Sending voice packets over your transport; push-to-talk; playing them through your mixer | \~70% |
| Voice playback | Your **mixer** (Layer 3) | — | Jitter buffer (smooth out late packets), per-player volume, mute, optional proximity voice (great for asymmetric games) | 0% |

**Learning-heavy alternative for voice:** use miniaudio capture + **libopus** (the codec used by most voice apps) + your own jitter buffer. It works outside Steam too, but it is roughly 3–4 extra weeks. Don't attempt echo cancellation; tell players to use headsets.

**Notes**

- Netcode is the hardest part of this project. Start it in month 3 with two local clients on one PC, never later.
- Build a network debug overlay in ImGui: ping, packet loss, bytes per second, snapshot buffer size.
- Keep the simulation **deterministic and tick-based**: same inputs + same tick = same result. Everything about networking gets easier.

## Layer 5 — Game (application) layer

**What this layer is:** everything that makes it *your* game rather than *a* game. The engine knows how to draw a sprite and move an entity. This layer decides that a player is a Hunter with a vision cone and a dash ability, or that a round ends when three generators are repaired. In a well-split project, this lives in `game/` and uses only engine interfaces, never SDL, OpenGL or Steam directly. Almost no libraries are needed. This layer is pure design + code.

| Area | Pick | Library does | You build and learn | Library share |
| --- | --- | --- | --- | --- |
| Roles (asymmetric core) | Write your own | — | Role definitions: abilities, speed, health, vision, win conditions. Loaded from JSON so you can tune without recompiling. | 0% (JSON parser aside) |
| Player controller | Write your own | — | Action inputs → movement with acceleration, facing, collisions; must work with network prediction | 0% |
| Abilities and interactions | Write your own | — | Cooldowns, interaction prompts ("hold E to repair"), timers, effects | 0% |
| Objectives and match rules | Write your own | — | Match flow: countdown → play → win check → results, all running on the server | 0% |
| Line of sight / fog of war | Write your own | — | Raycasts against wall tiles, visibility polygons ([Red Blob Games](https://www.redblobgames.com) has great guides), drawn as a lighting mask. Also drives interest management. | 0% |
| Camera behaviour | Write your own | — | Smooth follow, screen shake, role-specific zoom | 0% |
| Bots / AI | Write your own | — | Simple state machines (patrol → chase → search) + A\*. Essential for testing a multiplayer game alone. | 0% |
| HUD and menus | Your Layer 3 UI | — | Health, ability cooldowns, minimap, main menu, lobby, settings | 0% |
| Settings and saves | nlohmann/json + your file layer | Parsing | Key bindings, volumes, voice settings, resolution; saved in the OS user folder | \~30% |
| Game data | Tiled/LDtk + JSON | Editing UI | Maps, role stats, item tables | \~50% |

**Notes**

- **Design the asymmetry on paper first:** who are the roles, what can each see, what does each want? It drives networking (who receives what) and the UI.
- Keep mechanics simple (your stated goal), but keep **data-driven**: adding a new role should mean a new JSON file plus a few ability functions, not rewriting systems. That's your "scale later" plan.
- Prototype gameplay single-player in month 2 before netcode. If it's not fun locally, networking won't fix it.

## Layer 6 — Shipping on Steam (and later Epic)

**What this layer is:** turning your build into something strangers can buy, install and run on any of the three OSes. It has three parts: integrating store services in code, producing a correct build per OS, and the store's business process. Wrap every store feature behind your own `PlatformServices` interface (`createLobby`, `unlockAchievement`, `getUsername`). Then adding Epic later means writing a second implementation, not touching the game.

| Area | Pick | Library/tool does | You build and learn | Library share |
| --- | --- | --- | --- | --- |
| Store services | **Steamworks SDK** (native C++) | Login identity, lobbies, invites, voice, networking, achievements, cloud saves, overlay | `PlatformServices` wrapper, callback pumping, graceful behaviour when Steam isn't running | \~85% |
| Uploading builds | **SteamPipe** (`steamcmd` + build scripts) | Uploads and patches your game, one depot (content set) per OS | Writing the depot scripts; a CI job that uploads to a beta branch | \~90% |
| Windows build | MSVC, static or bundled runtime | — | Shipping the right DLLs (`steam_api64.dll`, SDL3); testing on a clean PC | — |
| macOS build | Clang, **universal binary** (Apple Silicon + Intel) | — | `.app` bundle, code signing + notarization (needs a paid Apple Developer account) | — |
| Linux build | **Steam Linux Runtime** SDK container | A stable set of libraries on every distro and the Steam Deck | Building inside the container; testing on Steam Deck if you can | \~80% |
| Crash reports | **sentry-native** (optional) | Captures crash dumps from players | Symbol upload, reading crash stacks | \~90% |
| Epic (later) | **Epic Online Services (EOS) SDK** | Same kind of services as Steamworks; also voice and cross-store lobbies | A second `PlatformServices` implementation | \~85% |

**Steam's business steps** (as of today, from [Steam Direct](https://partner.steamgames.com/steamdirect)):

1. Sign up for Steamworks and verify your identity, bank and tax details.
2. Pay the **$100 Steam Direct fee per game**. It is refunded once the game earns $1,000 adjusted gross revenue.
3. Wait **30 days** after paying before your first release is allowed. Start this around month 4.
4. Keep a public **"Coming Soon" store page for at least 2 weeks** before release, to collect wishlists.
5. Pass the build and store-page **review (1–5 days)**, then release when you choose.

**Notes**

- During development, put a `steam_appid.txt` next to the executable with your app ID. Never ship that file.
- Use Steam's free **Playtest** app or a private beta branch to test multiplayer with friends long before launch.
- Steam is the one store you need for v1. Epic can come after launch.

## 6-month plan and learning resources

The plan builds bottom-up but reaches something playable by the end of month 2, so you never spend long without a running game. Each month ends with a **gate**: a concrete demo you must reach before moving on. If a gate slips, cut scope (fewer abilities, one map), not layers.

&#91;embedded content: 6-month roadmap · one gate per month\]

Pay the Steam fee in month 4: the 30-day wait then ends before month 6, when your Coming Soon page needs its 2 weeks.

**Where your time will actually go** (rough estimate): engine systems \~35%, networking and voice \~30%, gameplay \~20%, tooling and shipping \~15%. Netcode is the riskiest part, which is why it starts in month 3, not month 5.

### Learning resources, in the order you'll need them

- [Game Programming Patterns](https://gameprogrammingpatterns.com): free book. Game loop, update method, component and state patterns. Read first.
- [SDL3 wiki](https://wiki.libsdl.org/SDL3): platform layer reference.
- [LearnOpenGL](https://learnopengl.com): the "Getting started" chapters are all you need for a 2D renderer.
- [Gaffer on Games](https://gafferongames.com): "Fix Your Timestep" (month 1), then the networking and serialization articles (month 3).
- [Red Blob Games](https://www.redblobgames.com): grids, A\* pathfinding, 2D visibility / line of sight.
- [Gabriel Gambetta: Fast-Paced Multiplayer](https://www.gabrielgambetta.com/client-server-game-architecture.html): the clearest explanation of prediction, reconciliation and interpolation.
- [Valve: Source Multiplayer Networking](https://developer.valvesoftware.com/wiki/Source_Multiplayer_Networking): how a shipped engine does it, including lag compensation.
- [Dear ImGui](https://github.com/ocornut/imgui) and [miniaudio](https://miniaud.io): read their example programs.
- [Steamworks documentation](https://partner.steamgames.com/doc/home): SDK, lobbies, networking sockets, voice, SteamPipe.
- [Handmade Hero](https://handmadehero.org) (optional, deep): one person writing a whole game engine from scratch in C-style C++, on video.
