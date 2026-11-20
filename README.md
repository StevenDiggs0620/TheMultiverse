# The Multiverse

This repository preserves the current upstream **The Universe** project as a
snapshot and provides a small, dependency-free tool for preparing release-only
launchers. The repository name remains **The Multiverse**; the first prerelease
is titled **The Universe full final release**.

## Start here

- `upstream/` mirrors the upstream file tree from TheUniverses commit
  `8c05c3fc83bad91313c48f39830d47b2db01e767`. The upstream has two case-only
  filename collisions (`PEAK`/`peak`); their original uppercase versions are
  preserved in `upstream-case-collisions/` because this Mac volume cannot store
  both names in the same folder. The release builder puts both exact names in
  the ZIP. Do not edit either snapshot folder as part of future Multiverse work.
- `release/START_HERE.md` explains what users receive and how to launch it.
- `release/manifest.json` lists release formats, requirements, and limitations.
- `tools/build_loaders.py` builds release artifacts with Python 3's standard
  library. Generated loaders are written under `dist/` and are not tracked by
  Git.

Build the release bundle with:

```sh
python3 tools/build_loaders.py
```

The command creates individual loaders under `dist/` and a combined ZIP beside
that folder. The ZIP contains the original project files under `Original Universe/`
and the launchers beside them. The primary loader is `dist/The-Universe.html`; it requires an
internet connection and opens the unchanged portal from the pinned upstream
snapshot, which is mirrored in this repo's `upstream/` folder. `--url` can override the portal URL when preparing a
release from another published commit.

## Attribution and rights

The upstream README credits **tasdiam**. This is a fork of
[TheUniverses](https://github.com/susybakaboiii/TheUniverses); the upstream tree
and its existing notices are preserved. No root license was present in the
upstream snapshot. The repository does not claim ownership of third-party games,
music, images, or other bundled material. Those materials may have separate
rights and terms; this README does not grant permission to redistribute them.

The loader builder creates transparent launchers and links. It does not change
the portal's code or bypass browser, document-reader, or operating-system
security controls. PDF, EPUB, and office formats may only provide a link; see
`release/manifest.json` for per-format limitations.
