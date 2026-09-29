"""在 llms.txt 每頁底下列出該頁的二級標題。

mkdocs-llmstxt 產生的 llms.txt 只有頁名，AI 從「迭代 14 分冊」這種頁名猜不到裡面有心情問卷，
就不會點進去讀（0929 實測 ChatGPT 讀完目錄就停了）。把小標列出來，AI 才知道該點哪一頁。

hook 在所有外掛之後執行，這時 llms.txt 與各頁的 index.md 都已經寫好了。
"""

from __future__ import annotations

import re
from pathlib import Path

_LINK = re.compile(r"^- \[[^\]]*\]\((?P<url>[^)]+)\)")
_H2 = re.compile(r"^## +(?P<text>.+?)\s*$")
_MD_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")


def _headings(md_file: Path) -> list[str]:
    out = []
    in_code = False
    for line in md_file.read_text(encoding="utf8").splitlines():
        if line.startswith("```"):
            in_code = not in_code
            continue
        m = None if in_code else _H2.match(line)
        if m:
            text = _MD_LINK.sub(r"\1", m["text"]).replace("*", "").strip()
            if text:
                out.append(text)
    return out


def on_post_build(config, **kwargs):
    site = Path(config.site_dir)
    llms = site / "llms.txt"
    if not llms.exists():
        return
    plugin = config.plugins.get("llmstxt")
    base = (plugin.config.base_url if plugin else None) or config.site_url
    base = base if base.endswith("/") else base + "/"

    lines = []
    for line in llms.read_text(encoding="utf8").splitlines():
        lines.append(line)
        m = _LINK.match(line)
        if not m or not m["url"].startswith(base):
            continue
        md_file = site / m["url"][len(base):]
        if md_file.exists():
            lines.extend(f"  - {h}" for h in _headings(md_file))
    llms.write_text("\n".join(lines) + "\n", encoding="utf8")
