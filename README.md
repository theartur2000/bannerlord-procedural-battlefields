# Procedural Battlefields

Procedural Battlefields is a mod for Mount & Blade II: Bannerlord that generates a new battle map for every field
battle in the campaign.

When a battle starts, the mod reads the campaign map around the player's party (biome, mountains, forest, rivers,
coast) and generates a matching map during the loading screen: terrain, rocks, vegetation, navigation mesh and spawn
positions. Generation takes 1.3 to 2.0 seconds on an Intel Core i5-12600KF.

![A generated valley](docs/images/valley.jpg)

| | |
|---|---|
| ![Steppe](docs/images/steppe.jpg) | ![River crossing](docs/images/crossing.jpg) |
| ![Mountain shelf in winter](docs/images/snow.jpg) | ![Desert](docs/images/desert.jpg) |

> [!NOTE]
> Procedural Battlefields is in early development. It is tested on Bannerlord v1.4.8 only, there is no packaged
> release yet, and it is not on the Steam Workshop. For now it has to be built from source.

## Features

- **Ten map layouts**: ridge, valley, hill, river crossing, forest clearing, mountain pass, coastal bluff, broken
  ground, desert mesas, and a mountain shelf with a lethal drop.
- **Natural terrain**: layered noise, domain warping, and fluvial and thermal erosion.
- **Native assets**: rocks, trees, grass and bushes from the game's own battle maps, placed and painted the way
  those maps do it. Rocks are fitted to the terrain from their actual mesh geometry.
- **Battle-ready**: navigation mesh, spawn paths, map border, and tactical markers for the AI.
- **Seasons**: snow cover in winter.
- **Custom asset support**: the generator can build a map from third-party models and textures only (see
  [Custom assets](#custom-assets)).
- **No dependencies**: no Harmony or other mods required. Nothing is stored in save games, so the mod can be added
  to or removed from an existing campaign.

## Requirements

| | |
|---|---|
| To play | Mount & Blade II: Bannerlord v1.4.8 (Windows, single player) |
| To build | Python 3.10 or later, the .NET SDK, and an installed copy of the game |
| Disk space | about 250 MB installed |

## Installation

```powershell
git clone --recursive https://github.com/theartur2000/bannerlord-procedural-battlefields
cd bannerlord-procedural-battlefields
pip install -r requirements.txt
$env:BANNERLORD_DIR = "<game folder>"             # not needed for the default Steam location

dotnet build mod/GenFields/src/GenFields.csproj -c Release -p:BannerlordDir="$env:BANNERLORD_DIR" -o build
python tools/livedata.py                          # one-time data export, takes a few minutes
python tools/install.py --dll build --live        # the game must be closed
```

Enable **GenFields** in the Bannerlord launcher.

`livedata.py` exports the data the generator needs (rock shapes, ground layer statistics, terrain samples) from the
local game install. This repository contains no game content.

To uninstall, run `python tools/install.py --remove`. The installer writes only inside `Modules\GenFields`.

## Usage

The mod works automatically in campaign field battles on land. Sieges, villages, hideouts and naval battles use the
game's own scenes.

| Action | How |
|---|---|
| Report a problem spot | Press **F10** in battle. The position and a screenshot are saved. |
| Disable generation | Create an empty file `genfields_nolive.txt` in `Modules\GenFields`. |
| Read the log | `Modules\GenFields\genfields_log.txt` |

A single map can also be generated offline and played in Custom Battle:

```powershell
python tools/procgen.py --biome Plain --kind valley --rugged 0.8 --forest 0.25 --seed 311 --name my_valley --preview my_valley.png
python tools/install.py --dll build --scene my_valley
```

## Known limitations

- Only plains, steppe and desert have dedicated data. Other regions, including the snowy north, currently generate
  as plains, and snow appears only in winter.
- Night battles, rain, and large battles with reinforcement waves are untested.
- The fairness of the two starting positions has not been measured.
- In steep valleys, some rocks are partly buried in the hillside.
- The engine keeps a loaded scene's terrain file open until the game exits. The mod can therefore generate about 60
  maps per biome per session; after that it uses the game's own scenes until the game is restarted.

## How it works

The mod wraps the campaign's `SceneModel`, which the game queries for the scene of each battle. For a land battle it
samples the terrain types around the party, derives a set of rules (biome, ruggedness, forest cover, water), selects
a layout, generates the map, and returns the name of the generated scene. All other queries are passed through.

The generator (`mod/GenFields/src/gen`) is plain C# with no engine calls. It writes the three files that make up a
Bannerlord scene: `scene.xscene`, `terrain.bin` and `navmesh.bin`.

Two engine constraints shape the design:

- A scene folder must exist when the game starts, although its files may be empty.
- Once a scene has been loaded, its `terrain.bin` stays open until the game exits.

The module therefore ships 64 scene folders per biome, most of them empty placeholders, and writes each new map into
an unused one. Used placeholders are cleared at the next start.

A Python reference implementation (`tools/procgen.py`) performs the same steps in 20 to 40 seconds and is easier to
experiment with. Changes to map generation should be made in both. `mod/GenFields/gen_cli` builds the C# generator
as a command-line program that reports the time taken by each step.

The design, measurements and engine findings are documented in [docs/BATTLEFIELDS.md](docs/BATTLEFIELDS.md).

## Tools

The Python tools are built on the
[Bannerlord Editor-Free SDK](https://github.com/theartur2000/bannerlord-editor-free-sdk), included as a submodule.
Each tool lists its options with `-h`.

| Script | Description |
|---|---|
| `tools/procgen.py` | Reference generator. Creates one map from rules or from a campaign map position, with a top-down preview. |
| `tools/livedata.py` | Exports the data the in-game generator needs from the local install. |
| `tools/install.py` | Installs or removes the module, single maps, the fallback pool and custom assets. |
| `tools/pool.py` | Pre-generates 24 fallback maps. |
| `tools/fieldmap.py` | Renders a top-down view of any Bannerlord battle scene. |
| `tools/lineup.py` | Creates a test scene showing every rock of a biome. |
| `tools/generate.py` | Earlier approach, kept for reference: cuts a map from the campaign map's own heights. |
| `tools/test.ps1` | Runs an unattended battle on a map, captures screenshots and exits. |
| `tools/bl2field.py` | Builds a map from custom assets only. |

## Custom assets

The generator accepts a palette of third-party ground textures, rocks and plants. `tools/bl2field.py` is a worked
example that builds a map exclusively from Borderlands 2 models and textures, read from a umodel export of a
user-owned copy of that game. None of those assets are included in this repository.

![A map built only from Borderlands 2 assets](docs/images/bl2field.jpg)

## Repository layout

```
mod/GenFields/      the module: SubModule.xml, C# source, the generator (src/gen), the command-line build (gen_cli)
tools/              Python generator, install and test scripts
docs/               design document and images
sdk/                Bannerlord Editor-Free SDK (git submodule)
```

## Acknowledgements

- Mount & Blade II: Bannerlord is developed by TaleWorlds Entertainment. This project is not affiliated with or
  endorsed by TaleWorlds.
- The fluvial erosion uses the implicit stream-power method of Braun and Willett (2013). Further references are
  listed in [docs/BATTLEFIELDS.md](docs/BATTLEFIELDS.md).
- Developed with Claude Code.

## License

Procedural Battlefields is released under the [MIT License](LICENSE).
