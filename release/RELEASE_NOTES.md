# The Universe full final release

This stable release packages the unchanged upstream project snapshot from TheUniverses commit
`8c05c3fc83bad91313c48f39830d47b2db01e767`. The repository remains named **The Multiverse**.
The release contains the pristine archive and a separate GitHub Pages runtime copy. In the
runtime copy, URLs that belonged to the original TheUniverses/ayosus hosting are redirected
to this repository. External game providers, APIs, fonts, and other third-party services may
still be required, so this release is not fully offline.

## Format results

These results describe the files generated for this release. The HTML and SVG approaches were
previously confirmed by the user to display the portal. Formats with variable support are not
represented as verified merely because a file was generated.
"Full launcher" means the portal page opens in the window; individual games are not all
independently verified. The preserved upstream catalog already points one thumbnail (`gn.png`)
to a file absent from its snapshot; this does not prevent the portal from opening.

### Full launchers — display the portal in the opened window

- **`The-Universe.html` and `The-Universe.htm`** — recommended; display the hosted portal in a
  full-window browser frame. The fallback link is shown only after a load failure or timeout.
- **`The-Universe.svg`** — displays the same portal using SVG `foreignObject`; support depends
  on the browser. The fallback link is hidden after successful loading.

### Link-only — open the portal from a clickable link

- **PDF, DOCX, RTF, ODT, PPTX, and ODP.** They do not run the portal inside the document. The
  PowerPoint file is regenerated for this release and its internal package links are checked.

### May not work as a launcher

- **MHT and MHTML** — included as requested, but the user reported both appear to do nothing.
- **XHTML, XHT, EPUB, XML, WebArchive, MAFF, and HTA** — viewer, browser, operating system, and
  security support varies; not confirmed as full launchers. HTA is Windows-specific.
- **ZIP** — this is a package, not an auto-launching file. Extract it and open the HTML loader.
- **DOC and PPT** — legacy binary formats are not generated.

## Internet and hosting

The launchers require internet access. The portal runtime is published from this repository's
`docs/universe/` folder. References to the original project's own hosted files are rewritten
to this GitHub Pages copy. Games can still rely on their own third-party services or embedded
providers, whose availability is outside this repository's control.

## Credit and rights

The upstream README credits **tasdiam**. The pristine snapshot and its notices are preserved.
The upstream repository has no root license file, and this release makes no new claim of
ownership or permission for third-party games, music, images, or services. Those may have
separate rights and terms.
