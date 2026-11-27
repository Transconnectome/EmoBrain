"""07_research_design.md에서 07_research_design.html을 다시 만든다(그림 PNG를 base64로 품은 한 파일 판).
변환은 Python-Markdown(확장 tables, sane_lists, fenced_code)이고, <head>는 지금 커밋된 HTML의 것을 그대로 쓴다.
abcdd95의 HTML을 바이트 단위로 재현하는 것을 확인한 방법이다(2026-11-26).
사용(레포 최상위에서): python docs/final/figures/src/build_07_html.py"""
import base64
import os
import re

import markdown

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
md_path, fig_dir, html_path = (os.path.join(D, "07_research_design.md"), os.path.join(D, "figures"),
                               os.path.join(D, "07_research_design.html"))
body = markdown.markdown(open(md_path, encoding="utf-8").read(), extensions=["tables", "sane_lists", "fenced_code"])
body = re.sub(r'src="figures/([^"]+\.png)"',
              lambda m: 'src="data:image/png;base64,' + base64.b64encode(open(os.path.join(fig_dir, m.group(1)), "rb").read()).decode() + '"', body)
old = open(html_path, encoding="utf-8").read()
head = old[:old.index("<body>") + len("<body>")]
open(html_path, "w", encoding="utf-8").write(head + body + "\n</body></html>\n")
print("written", html_path)
