# Procedural Battlefields for Bannerlord

A Mount & Blade II: Bannerlord mod (module id `GenFields`) that generates a new battlefield for every campaign field
battle. When a battle starts, the mod reads the world map around your party (biome, mountains, forest, rivers, coast),
generates terrain, rocks, forest, ground cover, navmesh and spawn lines for it, and sends the battle there. Nothing in a
field is hand-placed and no two battles share one. A field takes 1.3 to 1.8 seconds on the author's machine.

![A generated valley in the unmodified game](docs/images/valley.jpg)

| | |
|---|---|
| ![Steppe valley](docs/images/steppe.jpg) | ![River crossing](docs/images/crossing.jpg) |
| ![Mountain shelf in winter](docs/images/snow.jpg) | ![Desert](docs/images/desert.jpg) |

**No game content is included.** The screenshots show the game running. The generator's data (rock shapes, texture
layer statistics, relief samples) is written on your machine from your own install.

Built with the [Bannerlord editor-free SDK](https://github.com/theartur2000/bannerlord-editor-free-sdk), which writes
the scene, terrain and navmesh files without the Modding Kit editor.

## Status
A tech demo that runs, not a finished release. Written against Bannerlord v1.4.8.119303 (Steam, Windows, single
player); other versions are unverified.

Run in the game: campaign battles on generated fields in the plains, the steppe and the desert, including a river
crossing; 200 against 200 in Custom Battle on every layout; a winter field. Not yet checked: generated fields at night
and in rain, very large battles with reinforcement waves, how fair the two starting positions are, multiplayer (not
supported). There is no ready-to-install download yet: you build it from this source (below).

## What goes into a field
- **Layouts:** ridge, valley, hill, river crossing, forest clearing, mountain pass, coastal bluff, broken ground, mesas,
  and a mountain shelf with a sheer drop on one side (the game's own fall damage does the rest).
- **Natural shapes:** Perlin noise, domain warping, stream-power erosion with randomised downhill routing, thermal
  erosion, Poisson-disk scatter, and small relief quilted from the shipped battlefields of the biome.
- **Rocks that sit in the ground:** which rock, how big, how deep and turned which way is measured from the shipped
  scenes; each one is then fitted to the terrain from its real mesh and earth is banked over its open edges.
- **Ground cover:** every ground layer is painted as strongly and as widely as the shipped scene of the biome paints it,
  with its grass and plant models; rock textures are projected from six sides so cliffs do not stretch into stripes;
  winter shows the snow layers.
- **For the battle:** navmesh, spawn paths, a border, high-ground and chokepoint markers for the AI.

How each of these was measured and built is in [docs/BATTLEFIELDS.md](docs/BATTLEFIELDS.md).

## Requirements
To play: Bannerlord v1.4.8 with its own modules (Native, SandBoxCore, CustomBattle, Sandbox). No other mod and no
Harmony is needed. The mod wraps the game's scene model (`SceneModel`) and passes everything but land field battles on
to the model that was there before it. A mod loaded after it that replaces the scene model takes its place.

To build: Windows, Python 3.10 or newer, the .NET SDK (any version that can build `net472`), the game installed.

## Build and install
```powershell
git clone --recursive https://github.com/theartur2000/bannerlord-procedural-battlefields
cd bannerlord-procedural-battlefields
pip install -r requirements.txt
$env:BANNERLORD_DIR = "<your game folder>"       # not needed for the default Steam folder
python sdk/sdk/selftest.py                        # the SDK reads your install and changes nothing in it

dotnet build mod/GenFields/src/GenFields.csproj -c Release -p:BannerlordDir="$env:BANNERLORD_DIR" -o build
python tools/livedata.py                          # once, a few minutes: the generator's data, from your install
python tools/install.py --dll build --live        # game closed
```

Then enable "GenFields" in the launcher. `python tools/install.py --remove` deletes the module again. The installer
writes only inside `Modules\GenFields` and refuses while the game runs. The mod keeps nothing in save games: it can be
added to and removed from a running campaign.

`python tools/pool.py` followed by `install.py --pool` adds 24 ready-made fields as a fallback (about 30 seconds each
to generate).

## How it works in the game
`GenFieldSceneModel` (`mod/GenFields/src/SubModule.cs`) answers the game's question "which scene for this battle".
`Live.cs` samples the world map's terrain types on sixteen bearings around the party, derives the rules, and calls the
generator in `src/gen` (C#, no engine calls). The generator writes `scene.xscene`, `terrain.bin` and `navmesh.bin`
into a scene folder of the module and the game loads it like any shipped scene. Sieges, villages, hideouts, sea
battles and any terrain the mod has no data for keep the game's own scenes.

Two engine rules shape this:
- A scene folder has to exist when the game starts, but zero-byte scene files are enough then.
- Once a scene has been loaded, the engine keeps its `terrain.bin` open until the game exits.

So the module carries 64 scene folders a biome, 60 of them empty placeholders, and every battle writes into one not
yet used this session. Used placeholders are emptied at the next start. After 60 generated battles in one biome in one
session the mod falls back to the pool, and without a pool to the game's own scenes.

The speed comes from compiled loops over rows in parallel, box blurs in place of FFT Gaussians, data prepared ahead
by `livedata.py`, the erosion on a 257 x 257 grid, and PNGs written with one fixed filter and the fastest deflate.
`mod/GenFields/gen_cli` builds the same generator as a command-line program that prints the milliseconds of every step.

## Switches and files
All in `Modules\GenFields`:

| file | effect |
|---|---|
| `genfields_nolive.txt` | no generation in the game; the pool is used |
| `genfields_off.txt` | the pool is off too: the game's own scenes |
| `genfield.txt` | names one scene that every field battle goes to (testing) |
| `genfields_log.txt` | the mod's log: rules read from the map, the layout picked, milliseconds |

In a battle on a generated field the mod shows the field's layout once, and F10 writes your position to the log with a
screenshot. That is how a broken spot gets reported: stand on it and press F10.

## The tools
Python, built on the SDK. `python tools/<name>.py -h` lists the options.

| script | what it does |
|---|---|
| `tools/procgen.py` | the reference generator: a scene folder from rules (`--biome --kind --rugged --forest --water --seed`) or from a map position (`--map X Y`), with a top-view preview |
| `tools/livedata.py` | writes the data the in-game generator needs, from your install |
| `tools/pool.py` | generates the 24 pool fields |
| `tools/install.py` | installs the module, scenes, pool, live data and custom assets; `--remove` |
| `tools/fieldmap.py` | a top view of any scene folder: heights, layers, rocks, spawn lines |
| `tools/lineup.py` | a test scene with every rock of a biome standing alone |
| `tools/generate.py` | the first design, kept for reference: a field cut from the world map's own heights |
| `tools/bl2field.py` | the same generator fed only custom assets (below) |
| `tools/test.ps1` | one unattended run in the game with only this module, with screenshots |

The Python generator is the reference and takes 20 to 40 seconds a field; the C# one in the mod follows it step by
step. A change to how fields look goes into both.

```powershell
python tools/procgen.py --biome Plain --kind valley --rugged 0.8 --forest 0.25 --seed 311 --name my_valley --preview my_valley.png
python tools/install.py --dll build --scene my_valley       # lists it in Custom Battle
```

## A field made only of custom assets
`tools/bl2field.py` runs the generator with a palette of custom ground textures, rocks and plants, so nothing of
Bannerlord's is on the field. The worked example reads Borderlands 2 models and textures from umodel exports of your
own copy of that game; none of them are in this repository.

![A field built only from Borderlands 2 models and textures](docs/images/bl2field.jpg)

```powershell
python tools/bl2field.py --export <umodel export folder> --sets <ground texture sets> --kind valley --seed 7
python tools/install.py --dll build --scene bl2_field --assets "<SDK home>\stage\bl2field_assets"
```

## Known limits
- One version of the game tested. A game update that changes the scene or terrain format will need the SDK updated.
- Plains, steppe and desert have data. Forest, snow, mountain, canyon and swamp tiles of the map use the plains data
  (with more forest or more rock); winter comes from the season.
- In steep valleys some rocks still have terrain standing over part of their body. The mod lifts an agent found under
  the ground back onto it; that rescue has not been seen to trigger in play.
- 60 generated battles a biome a session (see above).
- Size: `--live` alone is about 250 MB installed (the data and four ready fields a biome) and grows by up to 15 MB a
  battle until the next start of the game empties the used slots. The pool adds about 15 MB a field.

## Layout
```
mod/GenFields/      SubModule.xml, src/ (the module), src/gen/ (the generator), gen_cli/ (the generator as a program)
tools/              the Python generator and the install and test scripts
docs/               BATTLEFIELDS.md (design, measurements, engine rules), images/
sdk/                the Bannerlord editor-free SDK, a git submodule
```

## Credits
- **TaleWorlds Entertainment** make Bannerlord; the game and everything in it belong to them.
- The erosion is the implicit stream-power scheme of Braun and Willett (2013) with a priority-flood fill. What other
  games do and what was read for the design is listed at the end of [docs/BATTLEFIELDS.md](docs/BATTLEFIELDS.md).
- Written with Claude Code (Opus 5.5) from the author's design and playtests.

## License
MIT, see `LICENSE`: use, change, sell or republish it; keep the copyright notice in copies.
