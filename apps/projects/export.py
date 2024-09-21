from typing import List, Dict

from docx import Document
from docx.shared import Cm, RGBColor

from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import re

a4width = 595.3


def styled_document() -> Document:
    """Create a new word doc with consistent styles"""
    doc = Document()

    # Modify the 'Normal' style to justify paragraphs, use modern font
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Inter"
    font.size = Pt(11)
    style.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY

    size_map = {"Heading 1": Pt(16), "Heading 2": Pt(14), "Heading 3": Pt(12)}
    for style in doc.styles:
        if "Heading" in style.name:
            # style.font.color.rgb = RGBColor(0xd7, 0x68, 0x01) #RGBColor(0xe4, 0x6f, 0x01)
            style.font.name = "Inter"
            style.font.color.rgb = RGBColor(0, 0, 0)
            style.font.size = size_map.get(style.name, style.font.size)

    # logo in header
    section = doc.sections[0]
    header = section.header
    paragraph = header.paragraphs[0]
    run = paragraph.add_run()
    import os

    imgfile = os.path.abspath("src/assets/img/bird-logo.png")
    assert os.path.isfile(imgfile)
    run.add_picture(imgfile, width=Cm(4.5))

    return doc


def interview_doc(
    title: str, messages: List[Dict[str, str]], metadata: Dict[str, str]
) -> Document:  # noqa: F821
    """
    Creates a word doc summarizing an interview

    Args:
        interview: interview object

    Returns:
        (unsaved) docx.Document object
    """
    document = styled_document()
    document.add_heading(title, level=1)

    # metadata section
    document.add_heading("Metadata", level=2)
    table = document.add_table(rows=1, cols=2)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Field"
    hdr_cells[1].text = "Value"
    for k, v in metadata.items():
        row_cells = table.add_row().cells
        row_cells[0].text = k
        row_cells[1].text = v or "Not provided"
    widths_cm = [6, 6]
    for c, w in enumerate(widths_cm):
        table.columns[c].width = Cm(w)
    table.allow_autofit = False
    table.autofit = False
    for j in range(len(table.rows)):
        for c, w in enumerate(widths_cm):
            table.cell(j, c).width = Cm(w)

    # messages section
    document.add_heading("Conversation", level=2)
    nrows = 1 + len(messages)
    table = document.add_table(rows=nrows, cols=3)
    for i, (w, t) in enumerate([(2, "Sender"), (12, "Message"), (2, "Time")]):
        table.columns[i].width = Cm(w)
        for j in range(nrows):
            table.cell(j, i).width = Cm(w)  # word ignores column widths
        table.cell(0, i).text = t
    for i, msg in enumerate(messages, 1):
        table.cell(i, 0).text = msg["sender"]
        table.cell(i, 1).text = msg["message"]
        table.cell(i, 2).text = msg["time"]
    table.allow_autofit = False
    table.autofit = False

    return document


# markdown to docx functions
# https://github.com/dnbt777/EasyModularScripts/blob/7dbe8e04f092aeacf2bd3d8235db4ab0013d6e57/media-tools/markdown_from_clipboard_to_docx.py#L8


def parse_markdown(md_text):
    lines = md_text.split("\n")
    parsed_lines = []

    for line in lines:
        if line.startswith("# "):
            parsed_lines.append(("heading1", line[2:]))
        elif line.startswith("## "):
            parsed_lines.append(("heading2", line[3:]))
        elif line.startswith("### "):
            parsed_lines.append(("heading3", line[4:]))
        elif line.startswith("#### "):
            parsed_lines.append(("heading4", line[5:]))
        elif line.startswith("##### "):
            parsed_lines.append(("heading5", line[6:]))
        elif line.startswith("###### "):
            parsed_lines.append(("heading6", line[7:]))
        elif line.startswith("* "):
            parsed_lines.append(("list_item", line[2:]))
        elif re.match(r"\d+\.\s", line):
            parsed_lines.append(("numbered_item", re.sub(r"\d+\.\s", "", line)))
        else:
            parsed_lines.append(("paragraph", line))

    return parsed_lines


def apply_formatting(paragraph, text):
    # Split the text by bold, italic, and underline markers
    parts = re.split(r"(\*\*.*?\*\*|\*.*?\*|_.*?_)", text)

    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            bold_run = paragraph.add_run(part[2:-2])
            bold_run.bold = True
        elif part.startswith("*") and part.endswith("*"):
            italic_run = paragraph.add_run(part[1:-1])
            italic_run.italic = True
        elif part.startswith("_") and part.endswith("_"):
            underline_run = paragraph.add_run(part[1:-1])
            underline_run.underline = True
        else:
            paragraph.add_run(part)


def add_to_document(doc, parsed_lines):
    for line_type, content in parsed_lines:
        if line_type == "heading1":
            p = doc.add_heading(level=1)
            apply_formatting(p, content)
        elif line_type == "heading2":
            p = doc.add_heading(level=2)
            apply_formatting(p, content)
        elif line_type == "heading3":
            p = doc.add_heading(level=3)
            apply_formatting(p, content)
        elif line_type == "heading4":
            p = doc.add_heading(level=4)
            apply_formatting(p, content)
        elif line_type == "heading5":
            p = doc.add_heading(level=5)
            apply_formatting(p, content)
        elif line_type == "heading6":
            p = doc.add_heading(level=6)
            apply_formatting(p, content)
        elif line_type == "list_item":
            p = doc.add_paragraph(style="List Bullet")
            apply_formatting(p, content)
        elif line_type == "numbered_item":
            p = doc.add_paragraph(style="List Number")
            apply_formatting(p, content)
        elif content:
            p = doc.add_paragraph()
            apply_formatting(p, content)


def append_markdown(doc, md_text):
    parsed_lines = parse_markdown(md_text)
    add_to_document(doc, parsed_lines)


def append_markdown_para(doc, md_text, style):
    """Append markdown for styled paragraph"""
    parsed_lines = parse_markdown(md_text)
    p = doc.add_paragraph(style=style)
    for _, content in parsed_lines:
        apply_formatting(p, content)


def add_toc(doc):
    """Adds a table of contents to the document.

    This dynamic field needs to be refreshed in Word when the document is
    loaded.
    """
    # https://stackoverflow.com/questions/18595864/python-create-a-table-of-contents-with-python-docx-lxml
    doc.add_heading("Contents", level=1)
    paragraph = doc.add_paragraph()
    run = paragraph.add_run()
    fldChar = OxmlElement("w:fldChar")  # creates a new element
    fldChar.set(qn("w:fldCharType"), "begin")  # sets attribute on element
    instrText = OxmlElement("w:instrText")
    instrText.set(qn("xml:space"), "preserve")  # sets attribute on element
    instrText.text = (
        'TOC \\o "1-2" \\h \\z \\u'  # change 1-3 depending on heading levels you need
    )

    fldChar2 = OxmlElement("w:fldChar")
    fldChar2.set(qn("w:fldCharType"), "separate")
    fldChar3 = OxmlElement("w:t")
    fldChar3.text = "Right-click to update field."
    fldChar2.append(fldChar3)

    fldChar4 = OxmlElement("w:fldChar")
    fldChar4.set(qn("w:fldCharType"), "end")

    for e in [fldChar, instrText, fldChar2, fldChar4]:
        run._r.append(e)
