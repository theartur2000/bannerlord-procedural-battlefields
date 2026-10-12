"""Puts the Bannerlord editor-free SDK on the import path. The tools here are built on it (scene, terrain and navmesh
files, the catalog of shipped scenes, rock fitting, asset packages): https://github.com/theartur2000/bannerlord-editor-free-sdk

Looked for, in this order: the folder named by BANNERLORD_SDK_DIR, the `sdk` folder of this repository (a git submodule:
git submodule update --init), a checkout named bannerlord-editor-free-sdk next to this repository."""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = None
for cand in (os.environ.get("BANNERLORD_SDK_DIR"), os.path.join(HERE, "..", "sdk"), os.path.join(HERE, "..", "..", "bannerlord-editor-free-sdk")):
    if cand and os.path.isfile(os.path.join(cand, "sdk", "terrain.py")): ROOT = os.path.abspath(cand); break
if ROOT is None:
    sys.exit("the SDK was not found: run  git submodule update --init  in this repository, or set BANNERLORD_SDK_DIR to a checkout of "
             "https://github.com/theartur2000/bannerlord-editor-free-sdk")
sys.path.insert(0, os.path.join(ROOT, "sdk"))
