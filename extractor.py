#!/usr/bin/env python3

import PyPDF2 as pypdf
from svglib.svglib import svg2rlg
import os.path
from reportlab.graphics import renderPDF
import img2pdf

# pypdf.PdfFileReader
from fpdf import FPDF

import urllib.request as url
import urllib.error

import re
import argparse

A4_WIDTH = 595 #pts
A4_HEIGHT = 842 #pts

REGEX = "href=\"flip\/", "_(?P<fn>\S*)\""

DATA = [
    {"name": "prozess", "cat":10},
    {"name": "checkliste", "cat": 9},
    {"name": "formular", "cat": 11},
    {"name": "mustertext", "cat": 15},
    {"name": "schulung", "cat": 17}
]
# change this
BASE_URL = "https://www.datenschutz minus in minus arztpraxen.de/"

def svg2pdf(infile, outfile=""):
    if outfile == "":
        out = os.path.splitext(infile)[0] + ".pdf"
    else:
        out = outfile
    # if os.path.isabs(out):
    #     out_abs = out
    # else:
    #     out_abs = os.path.join(os.getcwd(), out)
    drawing = svg2rlg(infile)
    renderPDF.drawToFile(drawing, out)


def png2pdf(infile, outfile=""):
    if outfile == "":
        out = os.path.splitext(infile)[0] + ".pdf"
    else:
        out = outfile
    # pdf = FPDF()
    # pdf.add_page()
    # pdf.image(infile)
    # pdf.output(out, "F")
    with open(out, "wb") as f:
        f.write(img2pdf.convert(infile))


def overlayPDFs(in1, in2, out):
    pass
    output = pypdf.PdfFileWriter()
    input1 = pypdf.PdfFileReader(open(in2, "rb"))

    page1 = input1.getPage(0)
    #page1.scaleTo(A4_WIDTH, A4_HEIGHT)
    ul = page1.mediaBox.upperLeft
    lr = page1.mediaBox.lowerRight
    width = lr[0] - ul[0]
    height = ul[1] - lr[1]
    watermark = pypdf.PdfFileReader(open(in1, "rb"))
    other = watermark.getPage(0)
    other.scaleTo(float(width), float(height))
    page1.mergePage(other)

    output.addPage(page1)

    outputStream = open(out, "wb")
    output.write(outputStream)
    outputStream.close()

def pdf_cat(input_files, output_file):
    merger = pypdf.PdfFileMerger()

    for pdf in input_files:
        merger.append(open(pdf, 'rb'))

    with open(output_file, 'wb') as fout:
        merger.write(fout)

def create_paths(htmldir):
    res = {}
    for d in DATA:
        res[d["name"]] = []
        path = os.path.join(htmldir, str(d["cat"]) + ".html")
        regex = re.compile(REGEX[0] + d["name"] + REGEX[1])
        for i, line in enumerate(open(path)):
            for match in re.finditer(regex, line):
                fn = match.group("fn")
                full_url = BASE_URL + "flip/" + d["name"] + "_" + fn + "/"
                res[d["name"]].append({"fn": fn, "url": full_url})
    return res

def build_document(basedir, name, url):
    dir = os.path.join(basedir, name)
    os.makedirs(dir)
    n = NetworkAdapter(dir)
    files = n.retrieveFiles(url)
    created_pdfs = []
    page = 0
    for f in files:
        bg_pdf = os.path.splitext(f["image"])[0] + ".pdf"
        text_pdf = os.path.splitext(f["text"])[0] + ".pdf"
        res_pdf = os.path.join(dir, "combined" + str(page).zfill(4))
        svg2pdf(f["text"], text_pdf)
        png2pdf(f["image"], bg_pdf)
        overlayPDFs(text_pdf, bg_pdf, res_pdf)
        created_pdfs.append(res_pdf)
        page += 1
    outfile = os.path.join(basedir, name + ".pdf")
    pdf_cat(created_pdfs, outfile)
    return outfile

class NetworkAdapter:

    def __init__(self, basedir ="/tmp"):
        self._basedir = basedir

    def retrieveFiles(self, baseurl):
        SVG_DIR = "files/assets/common/page-vectorlayers/"
        PNG_DIR = "files/assets/common/page-html5-substrates/"
        PAD_TO = 4
        results = []
        if not baseurl.endswith("/"):
            baseurl += "/"
        cnt = 1
        while True:
            try:
                svg_file = str(cnt).zfill(PAD_TO) + ".svg"
                svg_url = baseurl + SVG_DIR + svg_file
                svg_path = os.path.join(self._basedir, svg_file)
                url.urlretrieve(svg_url, svg_path)

                png_file = "page" + str(cnt).zfill(PAD_TO) + "_4.jpg"
                png_url = baseurl + PNG_DIR + png_file
                png_path = os.path.join(self._basedir, png_file)
                url.urlretrieve(png_url, png_path)

                results.append({"text": svg_path, "image": png_path})
                cnt += 1
            except urllib.error.HTTPError as e:
                #print("Could not find " + svg_url)
                break

        return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--htmldir", type=str, required=True)
    parser.add_argument("--outdir", type=str, required=True)
    args = parser.parse_args()
    r = create_paths(args.htmldir)
    for cat, doclist in r.items():
        catdir = os.path.join(args.outdir, cat)
        if not os.path.exists(catdir):
            os.makedirs(catdir)
        created_dirs = []
        for d in doclist:
            if not d["fn"] in created_dirs:
                res = build_document(catdir, d["fn"], d["url"])
                created_dirs.append(d["fn"])
                print("Wrote file " + res)
