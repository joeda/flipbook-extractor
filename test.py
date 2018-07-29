#!/usr/bin/env python3

import nose
import os

import extractor

def test_numbers_3_4():
    assert 3*4 == 12

def test_svg_to_pdf():
    svgpath = "res/0007.svg"
    extractor.svg2pdf(svgpath)
    assert os.path.isfile("res/0007.pdf")
    os.remove("res/0007.pdf")

def test_png_to_pdf():
    pngpath = "res/page0007_4.jpg"
    extractor.png2pdf(pngpath)
    assert os.path.isfile("res/page0007_4.pdf")
    os.remove("res/page0007_4.pdf")

def test_overlay():
    svgpath = "res/0007.svg"
    extractor.svg2pdf(svgpath)
    pngpath = "res/page0007_4.jpg"
    extractor.png2pdf(pngpath)
    pdf1 = "res/page0007_4.pdf"
    pdf2 = "res/0007.pdf"
    out = "res/mypdf.pdf"
    extractor.overlayPDFs(pdf2, pdf1, out)
    assert os.path.isfile(out)
    os.remove("res/page0007_4.pdf")
    os.remove("res/0007.pdf")
    os.remove(out)

def test_dl_content():
    base_url = "https://www.datenschutz-in-arztpraxen.de/flip/checkliste_einsatz_von_privaten_endgeraeten_byod/"
    nw = extractor.NetworkAdapter()
    res = nw.retrieveFiles(base_url)
    assert len(res) == 7
    assert os.path.isfile(res[6]["text"])
    assert os.path.isfile(res[2]["image"])