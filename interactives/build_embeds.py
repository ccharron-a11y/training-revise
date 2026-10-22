"""Build Litmos embed-code versions of five-whys-fishbone.html.

Usage: python3 -I build_embeds.py
Writes, next to this script:
  five-whys-fishbone.embed-snippet.html  scoped <div>+<style>+<script>, paste as embed code
  five-whys-fishbone.embed-iframe.html   one <iframe srcdoc>, fully isolated fallback
Edit the content in five-whys-fishbone.html, then re-run this script.
"""
import html
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
SRC = (HERE / "five-whys-fishbone.html").read_text(encoding="utf-8")
ROOT = "cx5why"
IDS = ["stepLabel", "title", "intro", "panel", "back", "next", "progress",
       "bones", "whys", "dgTitle", "dgDesc"]


def prefix_selectors(sel):
    out = []
    for s in sel.split(","):
        s = s.strip()
        if s in (":root", "html", "body"):
            s = f"#{ROOT}"
        elif s == "*":
            s = f"#{ROOT}, #{ROOT} *"
        else:
            s = f"#{ROOT} {s}"
        if s not in out:
            out.append(s)
    return ", ".join(out)


def harden(decls):
    """Mark declarations !important so host-page !important rules can't override them.
    Custom properties are left alone."""
    parts = []
    for d in decls.split(";"):
        if d.strip() and not d.strip().startswith("--") and "!important" not in d:
            d = d.rstrip() + " !important"
        parts.append(d)
    return ";".join(parts)


def scope_css(css):
    """Prefix every style rule's selectors with #ROOT, including rules nested in @media."""
    out, i, n = [], 0, len(css)
    while i < n:
        j = css.find("{", i)
        if j < 0:
            out.append(css[i:])
            break
        head = css[i:j].strip()
        if head.startswith("@"):
            out.append(f"\n{head} {{")
            # Find the matching close brace of the at-rule, scope its body recursively.
            depth, k = 1, j + 1
            while depth:
                depth += {"{": 1, "}": -1}.get(css[k], 0)
                k += 1
            out.append(scope_css(css[j + 1:k - 1]) + "\n}")
            i = k
        else:
            k = css.find("}", j)
            out.append(f"\n{prefix_selectors(head)} {{{harden(css[j + 1:k])}}}")
            i = k + 1
    return "".join(out)


style = re.search(r"<style>(.*?)</style>", SRC, re.S).group(1)
body = re.search(r"<body>(.*?)<script>", SRC, re.S).group(1)
script = re.search(r"<script>(.*?)</script>", SRC, re.S).group(1)

# Host pages restyle buttons, headings and lists; pin the basics.
resets = """
  :root { all: initial; display: block; }
  h3.cx5-h { font-size: 20px; font-weight: 700; line-height: 1.3; margin: 0 0 6px; padding: 0; border: 0; text-transform: none; letter-spacing: 0; color: var(--text); font-family: inherit; }
  p, ul, li { font-family: inherit; line-height: 1.45; }
  p { margin: 0; }
  button { line-height: 1.2; text-transform: none; letter-spacing: 0; box-shadow: none; min-width: 0; width: auto; height: auto; font-family: inherit; }
  svg text { font-family: inherit; }
  svg.diagram { max-width: none; min-width: 0; }
"""
css = scope_css(resets) + scope_css(style.replace("h1 {", "h3.cx5-h {"))

body = body.replace('<h1 id="title"></h1>', '<h3 class="cx5-h" id="title"></h3>')
for i in IDS:
    body = body.replace(f'id="{i}"', f'id="cx5-{i}"')
body = body.replace('aria-labelledby="dgTitle dgDesc"', 'aria-labelledby="cx5-dgTitle cx5-dgDesc"')

js = script
js = js.replace('document.getElementById("bones")', '$("bones")')
js = js.replace('document.getElementById("whys")', '$("whys")')
js = js.replace('const $ = id => document.getElementById(id);', '')
js = js.replace('{ id: "b-" + c.id }', '{ id: "cx5-b-" + c.id }')
js = js.replace('{ class: "why-node", id: "w" + i }', '{ class: "why-node", id: "cx5-w" + i }')
js = js.replace('$("title").focus?.();', '')
js = "(function () {\n  const $ = id => document.getElementById(\"cx5-\" + id);\n" + js + "\n})();"
assert "document.getElementById(id)" not in js

snippet = (f'<!-- 5 Whys fishbone interactive. Paste this whole block into a Litmos embed-code block. -->\n'
           f'<div id="{ROOT}">\n<style>{css}</style>\n{body.strip()}\n<script>{js}</script>\n</div>\n')
(HERE / "five-whys-fishbone.embed-snippet.html").write_text(snippet, encoding="utf-8")

iframe = ('<!-- 5 Whys fishbone interactive (isolated). Paste this into a Litmos embed-code block. -->\n'
          '<iframe title="Root cause: 5 Whys fishbone" style="width:100%;height:780px;border:0;" '
          'srcdoc="' + html.escape(SRC, quote=True) + '"></iframe>\n')
(HERE / "five-whys-fishbone.embed-iframe.html").write_text(iframe, encoding="utf-8")
print("snippet", len(snippet), "bytes; iframe", len(iframe), "bytes")
