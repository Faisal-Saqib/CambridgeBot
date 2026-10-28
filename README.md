# CambridgeBot

Rust and C++ bots for Cambridge Battlecode 2026a (CAMBC), built with the official `cambc` CLI. The SDK version is pinned in `cambc.toml`.

The latest released bot is **v24 guarded support** in `bots/apex` (also preserved in `bots/guarded`); `bots/apex22` is the rollback baseline. V24 is experimental: its local panel won 50/140 against v22, with zero bot faults. The [full strategy](docs/FULL_STRATEGY.md), [changelog](docs/CHANGELOG.md) and [strategy index](docs/README.md) describe the versions and results. The [protected Prism carry](docs/strategies/prism-carry-plan.md) is a proposal, not implemented in v24.

The C++ commands below apply to the legacy `bots/main` bot. For the current Rust bot, use `cambc build apex`. Credentials, personal files, build caches and raw match/replay bundles are excluded from this repository.

## Layout

| Path | What |
| --- | --- |
| `bots/apex/`, `bots/guarded/` | Latest released Rust bot: v24 guarded support (experimental). |
| `bots/apex22/` | Preserved v22 rollback baseline. |
| `bots/main/` | Legacy C++ bot. `src/main.cpp` dispatches to `draft.cpp` (draft phase) and `bot.cpp` (champion turns). |
| `bots/starter-cpp/` | Official starter bot, kept unchanged as a baseline opponent. |
| `sdk/` | SDK headers (`sdk/cpp/cambc.h`) and templates, written by `cambc init`. |
| `cmake/` | Shared CMake file `cambc build` uses for every C++ bot. |
| `scripts/gauntlet.py` | Plays a bot against an opponent on every map, from both sides. |
| `GameRules.md`, `BotAPICpp.md` | Exported game handbook and C++ API reference. |
| `maps/` | Published map pool, included in this repository. |
| `replays/`, `matches/` | Local replay and match output, excluded from Git. |

## Setup (Windows)

Requires the `cambc` CLI on PATH (`cambc --version`) and Python (`py --version`). In a fresh clone:

```powershell
cambc init --yes .
.\tasks.ps1 build
```

`cambc init` downloads wasi-sdk, cmake and ninja and pulls the map pool. It leaves `bots/` untouched.

## Everyday commands (PowerShell)

```powershell
.\tasks.ps1 build                         # compile bots/main to WASM
.\tasks.ps1 run                           # main vs starter-cpp on 00ambush
.\tasks.ps1 run -Map 00anvil -Opp main    # any map / opponent
.\tasks.ps1 view                          # open the latest replay in the visualiser
.\tasks.ps1 gauntlet                      # main vs starter-cpp on every map, both sides
.\tasks.ps1 maps                          # refresh the map pool
cambc login; .\tasks.ps1 submit           # upload bots/main to the platform
```

If PowerShell refuses to run the script, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once.

`gauntlet` and `release` build in release mode, which is what the platform uses. `run` uses debug mode, so `cambc::debug` drawing and logs work.

## Editor

Each bot has `.clangd` and a generated `compile_commands.json`, so clangd (for example VS Code's clangd extension) gets autocomplete for `cambc.h` after the first build.

## Upgrading the SDK

Update the `cambc` CLI, then run `cambc init --yes .` and commit the updated `sdk/` and `cambc.toml`.
