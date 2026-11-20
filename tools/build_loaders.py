#!/usr/bin/env python3
"""Build release-only launchers for the preserved upstream Universe snapshot.

Uses only Python's standard library. Generated files go to dist/ (git-ignored).
The documents are transparent launch pages/links; they do not conceal the
destination or bypass browser, reader, or operating-system security controls.
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
import plistlib
import shutil
import zipfile
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "upstream"
CASE_COLLISION_SOURCE = ROOT / "upstream-case-collisions"
DEFAULT_OUTPUT = ROOT / "dist"
DEFAULT_URL = (
    "https://cdn.jsdelivr.net/gh/susybakaboiii/TheUniverses@"
    "8c05c3fc83bad91313c48f39830d47b2db01e767/the-universe-test.html"
)
RELEASE_TITLE = "The Universe full final release"


def make_html(url: str, title: str, xhtml: bool = False) -> str:
    esc_url = html.escape(url, quote=True)
    esc_title = html.escape(title)
    if xhtml:
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head><title>{esc_title}</title><meta charset="UTF-8" />
<style type="text/css">html,body,iframe{{width:100%;height:100%;margin:0;border:0}}body{{background:#080611;color:white;font:16px sans-serif}}iframe{{position:fixed;inset:0;z-index:1}}p{{position:fixed;z-index:2;top:0;left:0;padding:.5rem;background:#171329}}</style>
</head><body><p><a href="{esc_url}">Open {esc_title}</a></p>
<iframe title="{esc_title}" src="{esc_url}"></iframe></body></html>
'''
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc_title}</title><style>html,body,iframe{{width:100%;height:100%;margin:0;border:0}}body{{background:#080611;color:white;font:16px system-ui,sans-serif}}iframe{{position:fixed;inset:0;z-index:1}}p{{position:fixed;z-index:2;top:0;left:0;padding:.5rem;background:#171329}}</style></head>
<body><p><a href="{esc_url}">Open {esc_title}</a></p><iframe title="{esc_title}" src="{esc_url}"></iframe></body></html>
'''


def make_svg(url: str) -> str:
    u = html.escape(url, quote=True)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xhtml="http://www.w3.org/1999/xhtml" width="100%" height="100%" viewBox="0 0 1280 720">
 <foreignObject x="0" y="0" width="1280" height="720"><xhtml:html><xhtml:head><xhtml:meta charset="utf-8"/><xhtml:style>html,body,iframe{{width:100%;height:100%;margin:0;border:0}}body{{background:#080611;color:white;font:16px sans-serif}}iframe{{position:fixed;inset:0;z-index:1}}p{{position:fixed;z-index:2;top:0;left:0;padding:.5rem;background:#171329}}</xhtml:style></xhtml:head>
 <xhtml:body><xhtml:p><xhtml:a href="{u}">Open The Universe</xhtml:a></xhtml:p><xhtml:iframe title="The Universe" src="{u}"/></xhtml:body></xhtml:html></foreignObject>
</svg>
'''


def make_xml(url: str) -> str:
    # XHTML in XML form. Browsers that don't render XHTML from .xml still show
    # the XML source, where the explicit URL remains visible and clickable.
    return make_html(url, "The Universe", xhtml=True)


def make_mhtml(url: str) -> bytes:
    boundary = "----=_TheUniverseLoader_7f3a"
    body = make_html(url, "The Universe").encode("utf-8")
    return (
        "MIME-Version: 1.0\r\n"
        f"Content-Type: multipart/related; type=\"text/html\"; boundary=\"{boundary}\"\r\n"
        "Subject: The Universe loader\r\n\r\n"
        f"--{boundary}\r\nContent-Type: text/html; charset=\"utf-8\"\r\n"
        "Content-Transfer-Encoding: 8bit\r\nContent-Location: index.html\r\n\r\n"
    ).encode("ascii") + body + f"\r\n--{boundary}--\r\n".encode("ascii")


def make_epub(url: str, path: Path) -> None:
    xhtml = make_html(url, "The Universe EPUB loader", xhtml=True)
    container = '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>'''
    opf = '''<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="id"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="id">the-universe-loader</dc:identifier><dc:title>The Universe loader</dc:title><dc:language>en</dc:language></metadata><manifest><item id="page" href="loader.xhtml" media-type="application/xhtml+xml" properties="scripted"/><item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/></manifest><spine><itemref idref="page"/></spine></package>'''
    nav = '''<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops"><head><title>Contents</title></head><body><nav epub:type="toc"><ol><li><a href="loader.xhtml">Open The Universe</a></li></ol></nav></body></html>'''
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", container)
        z.writestr("OEBPS/content.opf", opf)
        z.writestr("OEBPS/loader.xhtml", xhtml)
        z.writestr("OEBPS/nav.xhtml", nav)


def make_webarchive(url: str, path: Path) -> None:
    page = make_html(url, "The Universe Web Archive loader").encode("utf-8")
    archive = {
        "WebMainResource": {
            "WebResourceData": page,
            "WebResourceMIMEType": "text/html",
            "WebResourceURL": "https://example.invalid/the-universe-loader.html",
            "WebResourceTextEncodingName": "UTF-8",
        },
        "WebSubresources": [],
        "WebSubframeArchives": [],
    }
    path.write_bytes(plistlib.dumps(archive, fmt=plistlib.FMT_XML))


def make_maff(url: str, path: Path) -> None:
    # MAFF is a ZIP-based archive convention; current browsers generally need
    # a compatible archive extension to open it as a web page.
    page = make_html(url, "The Universe MAFF loader")
    rdf = '''<?xml version="1.0" encoding="UTF-8"?>
<RDF xmlns="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:MAF="http://maf.mozdev.org/">
 <Description><MAF:originalurl>https://example.invalid/the-universe-loader.html</MAF:originalurl><MAF:title>The Universe loader</MAF:title><MAF:archivetime>2026-11-20T00:00:00Z</MAF:archivetime><MAF:charset>UTF-8</MAF:charset><MAF:about>index.html</MAF:about></Description>
</RDF>'''
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("index.rdf", rdf)
        z.writestr("index.html", page)


def pdf_escape(value: str) -> bytes:
    return value.encode("cp1252", "replace").replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)")


def make_pdf(url: str, path: Path) -> None:
    lines = [
        "The Universe full final release",
        "PDF launcher (opens the portal in your browser)",
        "A PDF viewer cannot reliably run the live HTML portal inside this document.",
        "Use the clickable link below. Browser and PDF security settings may ask first.",
        url,
    ]
    content = b"BT /F1 18 Tf 54 735 Td " + b" ".join(b"(" + pdf_escape(lines[0]) + b") Tj 0 -34 Td" for _ in [0]) + b"\n"
    for line in lines[1:]:
        content += b"/F1 11 Tf (" + pdf_escape(line) + b") Tj 0 -28 Td\n"
    content += b"ET\n"
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R /Annots [6 0 R] >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" + content + b"endstream",
        b"<< /Type /Annot /Subtype /Link /Rect [54 600 558 630] /Border [0 0 0] /A << /S /URI /URI (" + pdf_escape(url) + b") >> >>",
    ]
    out = bytearray(b"%PDF-1.4\n%PDF\n")
    offsets = [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(len(out))
        out.extend(f"{i} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref = len(out)
    out.extend(f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode())
    for off in offsets[1:]:
        out.extend(f"{off:010d} 00000 n \n".encode())
    out.extend(f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    path.write_bytes(out)


def ooxml_text(text: str) -> str:
    return escape(text)


def make_docx(url: str, path: Path, powerpoint: bool = False) -> None:
    if powerpoint:
        types = '''<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/><Override PartName="/ppt/slides/slide1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/><Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/><Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/></Types>'''
        rels = '''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/></Relationships>'''
        pres = '''<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId2"/></p:sldMasterIdLst><p:sldIdLst><p:sldId id="256" r:id="rId1"/></p:sldIdLst><p:sldSz cx="9144000" cy="5143500"/><p:notesSz cx="6858000" cy="9144000"/></p:presentation>'''
        p_rels = '''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/></Relationships>'''
        srels = f'''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" Target="{html.escape(url, quote=True)}" TargetMode="External"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/></Relationships>'''
        layout = '''<p:sldLayout xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" type="blank" preserve="1"><p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>'''
        layout_rels = '''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/></Relationships>'''
        master = '''<p:sldMaster xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld><p:clrMap accent1="4F46E5" accent2="70AD47" accent3="5B9BD5" accent4="ED7D31" accent5="A5A5A5" accent6="FFC000" bg1="lt1" bg2="lt2" folHlink="folHlink" hlink="hlink" tx1="dk1" tx2="dk2"/><p:sldLayoutIdLst><p:sldLayoutId id="1" r:id="rId1"/></p:sldLayoutIdLst><p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles></p:sldMaster>'''
        master_rels = '''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/></Relationships>'''
        slide = f'''<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/><p:sp><p:nvSpPr><p:cNvPr id="2" name="Title"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:t>The Universe full final release</a:t></a:r></a:p><a:p><a:r><a:t>Open the current Universe portal in your browser:</a:t></a:r></a:p><a:p><a:hlinkClick r:id="rId1"/><a:r><a:rPr><a:hlinkClick r:id="rId1"/></a:rPr><a:t>{ooxml_text(url)}</a:t></a:r></a:p><a:p><a:r><a:t>This presentation provides a link; it does not run the portal inside PowerPoint.</a:t></a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>'''
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("[Content_Types].xml", types)
            z.writestr("_rels/.rels", rels)
            z.writestr("ppt/presentation.xml", pres)
            z.writestr("ppt/_rels/presentation.xml.rels", p_rels)
            z.writestr("ppt/slides/slide1.xml", slide)
            z.writestr("ppt/slides/_rels/slide1.xml.rels", srels)
            z.writestr("ppt/slideLayouts/slideLayout1.xml", layout)
            z.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", layout_rels)
            z.writestr("ppt/slideMasters/slideMaster1.xml", master)
            z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", master_rels)
        return
    types = '''<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>'''
    rels = '''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'''
    link = f'''<w:p><w:hyperlink r:id="rId2"><w:r><w:rPr><w:color w:val="0563C1"/><w:u w:val="single"/></w:rPr><w:t>{ooxml_text(url)}</w:t></w:r></w:hyperlink></w:p>'''
    document = f'''<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><w:body><w:p><w:r><w:rPr><w:b/></w:rPr><w:t>The Universe full final release</w:t></w:r></w:p><w:p><w:r><w:t>Open the current Universe portal in your browser:</w:t></w:r></w:p>{link}<w:p><w:r><w:t>This document provides a link; it does not run the portal inside Word.</w:t></w:r></w:p><w:sectPr/></w:body></w:document>'''
    docrels = f'''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" Target="{html.escape(url, quote=True)}" TargetMode="External"/></Relationships>'''
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", types)
        z.writestr("_rels/.rels", rels)
        z.writestr("word/document.xml", document)
        z.writestr("word/_rels/document.xml.rels", docrels)


def make_rtf(url: str, path: Path) -> None:
    safe = url.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")
    path.write_text(r"{\rtf1\ansi\deff0 {\fonttbl{\f0 Arial;}}\fs30 The Universe full final release\par\par\fs22 Open the current portal in your browser:\par {\field{\*\fldinst HYPERLINK \"" + safe + r"\"}{\fldrslt\ul " + safe + r"}}\par\par This document provides a link; it does not run the portal inside Word.}", encoding="ascii")


def make_odt(url: str, path: Path) -> None:
    mimetype = "application/vnd.oasis.opendocument.text"
    content = f'''<?xml version="1.0" encoding="UTF-8"?><office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:xlink="http://www.w3.org/1999/xlink" office:version="1.3"><office:body><office:text><text:p>The Universe full final release</text:p><text:p>Open the current portal in your browser:</text:p><text:p><text:a xlink:type="simple" xlink:href="{html.escape(url, quote=True)}">{escape(url)}</text:a></text:p><text:p>This document provides a link; it does not run the portal inside the document.</text:p></office:text></office:body></office:document-content>'''
    manifest = '''<?xml version="1.0" encoding="UTF-8"?><manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0" manifest:version="1.3"><manifest:file-entry manifest:full-path="/" manifest:media-type="application/vnd.oasis.opendocument.text"/><manifest:file-entry manifest:full-path="content.xml" manifest:media-type="text/xml"/></manifest:manifest>'''
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("mimetype", mimetype, compress_type=zipfile.ZIP_STORED)
        z.writestr("content.xml", content)
        z.writestr("META-INF/manifest.xml", manifest)


def make_odp(url: str, path: Path) -> None:
    mimetype = "application/vnd.oasis.opendocument.presentation"
    content = f'''<?xml version="1.0" encoding="UTF-8"?><office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" office:version="1.3"><office:body><office:presentation><draw:page draw:name="Slide 1" draw:style-name="dp1" presentation:presentation-page-layout-name="AL1"><draw:frame draw:style-name="fr1" draw:text-style-name="P1" svg:width="25cm" svg:height="8cm" svg:x="2cm" svg:y="3cm"><draw:text-box><text:p>The Universe full final release</text:p><text:p>Open the portal in your browser:</text:p><text:p><text:a xlink:type="simple" xlink:href="{html.escape(url, quote=True)}">{escape(url)}</text:a></text:p><text:p>This presentation provides a link; it does not run the portal inside the presentation.</text:p></draw:text-box></draw:frame></draw:page></office:presentation></office:body></office:document-content>'''
    styles = '''<?xml version="1.0" encoding="UTF-8"?><office:document-styles xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0" office:version="1.3"><office:styles/><office:automatic-styles><style:page-layout style:name="PL1"><style:page-layout-properties fo:page-width="28cm" fo:page-height="21cm" xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"/></style:page-layout><style:style style:name="dp1" family="drawing-page"><style:drawing-page-properties presentation:display-header="false" presentation:display-footer="false"/></style:style><style:style style:name="fr1" family="graphic"/></office:automatic-styles><office:master-styles><draw:layer-set><draw:layer draw:name="layout"/><draw:layer draw:name="background"/><draw:layer draw:name="backgroundobjects"/><draw:layer draw:name="controls"/><draw:layer draw:name="measurelines"/></draw:layer-set><style:master-page style:name="Default"/></office:master-styles></office:document-styles>'''
    manifest = '''<?xml version="1.0" encoding="UTF-8"?><manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0" manifest:version="1.3"><manifest:file-entry manifest:full-path="/" manifest:media-type="application/vnd.oasis.opendocument.presentation"/><manifest:file-entry manifest:full-path="content.xml" manifest:media-type="text/xml"/><manifest:file-entry manifest:full-path="styles.xml" manifest:media-type="text/xml"/></manifest:manifest>'''
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("mimetype", mimetype, compress_type=zipfile.ZIP_STORED)
        z.writestr("content.xml", content)
        z.writestr("styles.xml", styles)
        z.writestr("META-INF/manifest.xml", manifest)


def make_start_here(path: Path, url: str) -> None:
    path.write_text(f'''THE UNIVERSE FULL FINAL RELEASE

START HERE

For the most reliable launch, open The-Universe.html in a current browser while online.
The SVG and HTML-family loaders are launchers. They load the portal from this pinned
upstream snapshot:
{url}

The portal, games, and some services need an internet connection. Some linked games or
services may have their own availability, browser, or licensing limits.

All files under Original Universe/ in the combined ZIP are the upstream project
snapshot. The loader files and this guide are release packaging, not edits to the portal. Creator credit and all
upstream notices are retained. No new license or ownership claim is made for bundled
third-party games, media, or services.

The upstream tree has filenames that differ only by case (PEAK/peak). The ZIP keeps
both original names, but a case-insensitive drive may overwrite one when extracting.

PDF, EPUB, Word, and PowerPoint files provide reader-friendly launch attempts or links;
they do not reliably execute the portal inside those document readers. See manifest.json
for the format-by-format notes. If one of those readers blocks the link, use the HTML file.
''', encoding="utf-8")


FORMAT_NOTES = {
    "html": "Direct iframe launcher; recommended. Requires a browser and internet access.",
    "htm": "Same HTML launcher as .html.",
    "xhtml": "XHTML iframe launcher; XML/XHTML support varies by browser.",
    "xht": "Same XHTML launcher as .xhtml.",
    "mht/mhtml": "Single-part MHTML launcher; opening and remote iframe behavior vary by browser.",
    "svg": "Uses SVG foreignObject and an iframe; browser support varies.",
    "pdf": "Clickable external launch link. PDF readers do not reliably run the live portal inside the PDF.",
    "epub": "XHTML launch attempt plus a link; ebook readers commonly restrict scripts, frames, or network access.",
    "xml": "XHTML content in an XML file; rendering varies and source may be shown instead.",
    "zip": "Contains an HTML launcher and release guide; extract it and open index.html online.",
    "webarchive": "Safari WebArchive containing an HTML launcher; remote content behavior varies.",
    "maff": "ZIP-based Mozilla Archive Format attempt; requires compatible software/extension and internet access.",
    "hta": "Windows HTML Application launcher; only open if you trust the source. Windows security policy may block it.",
    "docx": "Clickable external link only; Word does not execute the portal inside the document.",
    "doc": "Legacy binary Word format is not generated by this dependency-free builder.",
    "rtf": "Clickable external link only.",
    "odt": "Clickable external link only.",
    "pptx": "Clickable external link on one slide; PowerPoint does not execute the portal inside the presentation.",
    "ppt": "Legacy binary PowerPoint format is not generated by this dependency-free builder.",
    "odp": "Clickable external link only; presentation software does not run the portal inside the presentation.",
}


def build(source: Path, output: Path, url: str, include_snapshot: bool) -> None:
    portal = source / "the-universe-test.html"
    if not portal.is_file():
        raise SystemExit(f"Missing upstream portal: {portal}")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    products = {
        "The-Universe.html": make_html(url, "The Universe"),
        "The-Universe.htm": make_html(url, "The Universe"),
        "The-Universe.xhtml": make_html(url, "The Universe", xhtml=True),
        "The-Universe.xht": make_html(url, "The Universe", xhtml=True),
        "The-Universe.svg": make_svg(url),
        "The-Universe.xml": make_xml(url),
        "The-Universe.hta": "<!doctype html>\n<html><head><meta charset=\"utf-8\"><title>The Universe</title><hta:application id=\"UniverseLoader\" applicationname=\"The Universe loader\" border=\"thin\" caption=\"yes\" showintaskbar=\"yes\" singleinstance=\"yes\" sysmenu=\"yes\" windowstate=\"maximize\"/><style>html,body,iframe{width:100%;height:100%;margin:0;border:0}body{background:#080611;color:white;font:16px sans-serif}iframe{position:fixed;inset:0}</style></head><body><p><a href=\"" + html.escape(url, quote=True) + "\">Open The Universe</a></p><iframe title=\"The Universe\" src=\"" + html.escape(url, quote=True) + "\"></iframe></body></html>\n",
    }
    for filename, contents in products.items():
        (output / filename).write_text(contents, encoding="utf-8")
    for filename in ("The-Universe.mht", "The-Universe.mhtml"):
        (output / filename).write_bytes(make_mhtml(url))
    make_epub(url, output / "The-Universe.epub")
    make_pdf(url, output / "The-Universe.pdf")
    make_webarchive(url, output / "The-Universe.webarchive")
    make_maff(url, output / "The-Universe.maff")
    make_docx(url, output / "The-Universe.docx")
    make_docx(url, output / "The-Universe.pptx", powerpoint=True)
    make_rtf(url, output / "The-Universe.rtf")
    make_odt(url, output / "The-Universe.odt")
    make_odp(url, output / "The-Universe.odp")
    make_start_here(output / "START_HERE.txt", url)
    notes_source = ROOT / "release" / "RELEASE_NOTES.md"
    notes = notes_source.read_text(encoding="utf-8") if notes_source.is_file() else "See START_HERE.txt and manifest.json.\n"
    (output / "RELEASE_NOTES.txt").write_text(notes, encoding="utf-8")
    manifest = {
        "release": RELEASE_TITLE,
        "project": "The Multiverse",
        "upstream_project": "The Universe",
        "upstream_creator_credit": "tasdiam (as credited by upstream README)",
        "upstream_repository": "https://github.com/susybakaboiii/TheUniverses",
        "upstream_snapshot_commit": "8c05c3fc83bad91313c48f39830d47b2db01e767",
        "portal_loader_target": url,
        "internet_required": True,
        "original_project_files": "Original Universe/ inside the combined ZIP (upstream snapshot, unmodified; exact-case duplicate names retained)",
        "release_packaging_files": "The-Universe.* plus START_HERE.txt and manifest.json",
        "formats": FORMAT_NOTES,
        "rights_note": "No new license or ownership claim is made. Third-party games, media, and services may have separate rights.",
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    package = output.parent / "The-Universe-full-final-release.zip"
    if package.exists():
        package.unlink()
    with zipfile.ZipFile(package, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for item in sorted(output.rglob("*")):
            if item.is_file():
                z.write(item, Path("The Universe full final release") / item.relative_to(output))
        if include_snapshot:
            ignored = {".DS_Store", "Thumbs.db", "desktop.ini"}
            for item in sorted(source.rglob("*")):
                if item.is_file() and item.name not in ignored:
                    z.write(item, Path("The Universe full final release/Original Universe") / item.relative_to(source))
            # APFS/OneDrive is case-insensitive here; store the two upstream
            # case-colliding originals outside the mirror and add them to ZIP
            # under their exact upstream paths without materializing them.
            collisions = {
                CASE_COLLISION_SOURCE / "PEAK.html": "PEAK.html",
                CASE_COLLISION_SOURCE / "PEAK.png": "thumbs/PEAK.png",
            }
            for item, relative in collisions.items():
                if not item.is_file():
                    raise SystemExit(f"Missing preserved case-collision file: {item}")
                z.write(item, Path("The Universe full final release/Original Universe") / relative)
    print(f"Built release artifacts in {output}")
    print(f"Created combined release package: {package}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="pristine upstream snapshot folder")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="release artifacts folder (git-ignored)")
    parser.add_argument("--url", default=DEFAULT_URL, help="public URL for the upstream portal file")
    parser.add_argument("--include-snapshot", dest="include_snapshot", action="store_true", default=True, help="include the complete upstream tree under Original Universe/ in the ZIP (default)")
    parser.add_argument("--without-snapshot", dest="include_snapshot", action="store_false", help="build launchers only, without the upstream file tree")
    args = parser.parse_args()
    build(args.source.resolve(), args.output.resolve(), args.url, args.include_snapshot)


if __name__ == "__main__":
    main()
