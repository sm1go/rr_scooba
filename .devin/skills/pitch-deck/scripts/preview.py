"""Render a PDF deck into contact sheets (4 slides per image) for visual QA.

Usage: python preview.py <deck.pdf> <out_dir>
Look at every sheet: clipped text, empty halves, tiny screenshots, broken images.
"""
import os, sys
import pymupdf


def main(pdf, out):
    os.makedirs(out, exist_ok=True)
    doc = pymupdf.open(pdf)
    print(len(doc), "pages", doc[0].rect)
    for g in range(0, len(doc), 4):
        pix = [doc[k].get_pixmap(dpi=40) for k in range(g, min(g + 4, len(doc)))]
        w, h = pix[0].width, pix[0].height
        sheet = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, w * 2 + 10, h * 2 + 10), False)
        sheet.clear_with(60)
        for j, p in enumerate(pix):
            p.set_origin((j % 2) * (w + 10), (j // 2) * (h + 10))
            sheet.copy(p, p.irect)
        path = os.path.join(out, f"sheet-{g // 4 + 1}.png")
        sheet.save(path)
        print(path, f"slides {g + 1}-{g + len(pix)}")


if __name__ == "__main__":
    main(*sys.argv[1:])
