import fitz  # PyMuPDF
import chromadb
import re
import requests
from pathlib import Path
from collections import Counter
from bs4 import BeautifulSoup, NavigableString

# ---- knobs ----
DOCUMENTS_DIR = Path("documents")
COLLECTION    = "my_collection"
TARGET_WORDS  = 350
OVERLAP_WORDS = 60

# web pages to ingest (MkDocs course site). name = clean id/source label.
WEB_DOCS = [
    ("tut00-remote-access", "https://cornell-ece2300.github.io/ece2300-mkdocs/ece2300-tut00-remote-access/"),
    ("tut01-linux",         "https://cornell-ece2300.github.io/ece2300-mkdocs/ece2300-tut01-linux/"),
    ("tut02-git",           "https://cornell-ece2300.github.io/ece2300-mkdocs/ece2300-tut02-git/"),
    ("coding-conventions",  "https://cornell-ece2300.github.io/ece2300-mkdocs/ece2300-coding-conventions/"),
    ("fpga-primer",         "https://cornell-ece2300.github.io/ece2300-mkdocs/ece2300-fpga-primer/"),
]

chroma_client = chromadb.PersistentClient(path="./chroma_db")
try:
    chroma_client.delete_collection(name=COLLECTION)
except Exception:
    pass
collection = chroma_client.get_or_create_collection(name=COLLECTION)


# ============================ shared chunking ============================
def chunk_words(text, target=TARGET_WORDS, overlap=OVERLAP_WORDS):
    words = text.split()
    if not words:
        return []
    if len(words) <= target:
        return [" ".join(words)]
    step = max(1, target - overlap)
    out = []
    for start in range(0, len(words), step):
        out.append(" ".join(words[start:start + target]))
        if start + target >= len(words):
            break
    return out


# ============================ PDF path ============================
NUMBERED_HEADING = re.compile(r"^\d+(\.\d+)*\.?\s+\S")


def parse_pdf(path):
    lines, raw_chars = [], 0
    with fitz.open(path) as pdf:
        n_pages = pdf.page_count
        for page in pdf:
            raw_chars += len(page.get_text().strip())
            for block in page.get_text("dict")["blocks"]:
                for line in block.get("lines", []):
                    spans = line.get("spans", [])
                    text = "".join(s["text"] for s in spans).strip()
                    if not text:
                        continue
                    size = max(s["size"] for s in spans)
                    lines.append({"text": text, "size": round(size, 1),
                                  "page": page.number + 1})
    if not lines:
        print(f"    !! {path.name}: {n_pages} pages but {raw_chars} text chars "
              f"-> likely image-only (needs OCR), skipping")
        return []

    counts = Counter()
    for ln in lines:
        counts[ln["size"]] += len(ln["text"])
    body_size = counts.most_common(1)[0][0]

    def is_heading(line):
        big = line["size"] >= body_size * 1.15 and len(line["text"].split()) <= 12
        num = bool(NUMBERED_HEADING.match(line["text"])) and len(line["text"].split()) <= 12
        return big or num

    sections, current = [], None
    for ln in lines:
        if is_heading(ln):
            current = {"heading": ln["text"], "page": ln["page"], "body": []}
            sections.append(current)
        else:
            if current is None:
                current = {"heading": "", "page": ln["page"], "body": []}
                sections.append(current)
            current["body"].append(ln["text"])

    stem, source = path.stem, path.name
    chunks, idx = [], 0
    for sec in sections:
        body_text = " ".join(sec["body"]).strip()
        if not body_text:
            continue
        for piece in chunk_words(body_text):
            text = f"{sec['heading']}\n{piece}" if sec["heading"] else piece
            chunks.append({"id": f"{stem}_{idx}", "text": text, "page": sec["page"],
                           "section": sec["heading"], "source": source})
            idx += 1
    return chunks


# ============================ HTML path ============================
def _clean(el):
    return " ".join(el.get_text().split())


def _walk(node, out):
    for child in node.children:
        if isinstance(child, NavigableString):
            continue
        name = child.name
        if name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            out.append(("heading", _clean(child)))
        elif name == "pre":
            out.append(("code", child.get_text().strip("\n")))
        elif name == "p":
            txt = _clean(child)
            if txt:
                out.append(("prose", txt))
        elif name in ("ul", "ol"):
            for li in child.find_all("li", recursive=False):
                txt = _clean(li)
                if txt:
                    out.append(("prose", "- " + txt))
        else:
            _walk(child, out)


def parse_html(name, url):
    html = requests.get(url, timeout=30).text
    soup = BeautifulSoup(html, "html.parser")
    article = soup.find("article") or soup.body or soup
    for a in article.select("a.headerlink"):
        a.decompose()

    blocks = []
    _walk(article, blocks)

    sections, current = [], {"heading": "", "blocks": []}
    for kind, content in blocks:
        if kind == "heading":
            if current["blocks"]:
                sections.append(current)
            current = {"heading": content, "blocks": []}
        else:
            current["blocks"].append((kind, content))
    if current["blocks"]:
        sections.append(current)

    source = f"{name}.html"
    chunks, idx = [], 0

    def emit(heading, body):
        nonlocal idx
        text = f"{heading}\n{body}" if heading else body
        chunks.append({"id": f"{name}_{idx}", "text": text, "page": 1,
                       "section": heading, "source": source, "url": url})
        idx += 1

    for sec in sections:
        merged = []
        for kind, content in sec["blocks"]:
            if kind == "prose" and merged and merged[-1][0] == "prose":
                merged[-1] = ("prose", merged[-1][1] + " " + content)
            else:
                merged.append((kind, content))
        for kind, content in merged:
            if kind == "prose":
                for piece in chunk_words(content):
                    emit(sec["heading"], piece)
            else:
                emit(sec["heading"], f"```\n{content}\n```")
    return chunks


# ============================ run ============================
all_chunks = []

print("PDFs:")
for pdf in sorted(DOCUMENTS_DIR.glob("*.pdf")):
    recs = parse_pdf(pdf)
    print(f"  {pdf.name:<40} {len(recs):>4} chunks")
    all_chunks.extend(recs)

print("Web pages:")
for name, url in WEB_DOCS:
    try:
        recs = parse_html(name, url)
        print(f"  {name:<40} {len(recs):>4} chunks")
        all_chunks.extend(recs)
    except Exception as e:
        print(f"  {name:<40} FAILED: {e}")

# chroma metadata can't hold None; keep url only when present
def meta(c):
    m = {"page": c["page"], "section": c["section"], "source": c["source"]}
    if "url" in c:
        m["url"] = c["url"]
    return m

collection.upsert(
    ids=[c["id"] for c in all_chunks],
    documents=[c["text"] for c in all_chunks],
    metadatas=[meta(c) for c in all_chunks],
)
print(f"\nStored {len(all_chunks)} chunks total in '{COLLECTION}'.")

# smoke test
for q in ["How many TAs are there?",
          "How do I log into the ecelinux servers with SSH?"]:
    r = collection.query(query_texts=[q], n_results=8)
    print(f"\nQUESTION: {q}")
    for i in range(len(r["documents"][0])):
        m = r["metadatas"][0][i]
        print(f"  {r['ids'][0][i]} | {m['source']} | {m.get('section')}")