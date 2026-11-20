# The Multiverse

The Multiverse is a fork of [TheUniverses](https://github.com/susybakaboiii/TheUniverses). It keeps the upstream portal and its game/service features while organizing the repository for future changes.

## Start here

- multiverse.svg — SVG loader for the current portal.
- multiverse.html — HTML loader for the same portal.
- portal/the-universe-test.html — current full-featured portal source.
- portal/the_universe.html — earlier stripped-down portal source.

The loaders fetch the portal from the main branch through jsDelivr. Publish the repository before expecting the loaders to resolve. For a direct source edit, work in portal/; the game catalog used by the full portal is data/catalogs/tas6.json.

## Repository layout

- games/ — standalone game wrapper pages.
- services/ — chat and TAS viewer pages.
- tabs/ — portal tabs, music, movies, and supporting data.
- assets/thumbs/ — game thumbnails.
- assets/ruffle/ — bundled Ruffle runtime and license notices.
- assets/godzilla/ — multipart Godzilla asset files.
- assets/source-svg/ — supplied SVG reference.
- data/catalogs/ — game list JSON files and legacy catalog variants.
- data/status/ — status/availability JSON files.
- data/messages.txt — rotating portal messages.
- docs/screenshots/ — screenshots from the upstream project.
- tools/ — repository helper scripts.

Game wrappers use explicit upstream base URLs where needed so moving them into games/ does not change their asset origins. Catalog entries point to this fork and the new paths.

## Attribution and asset rights

This is a fork of TheUniverses by susybakaboiii; its README credits tasdiam. The upstream repository has no root license file. Game pages, music, images, and other bundled materials may have separate rights. This repository does not claim ownership of third-party content. Check source and license terms before redistributing a release. Ruffle's license notices are in assets/ruffle/.

## Local housekeeping

.DS_Store, Thumbs.db, and desktop.ini are ignored. Same-content duplicate game wrappers were consolidated after verifying their file hashes; legacy JSON catalog variants remain in place to avoid breaking older references.
