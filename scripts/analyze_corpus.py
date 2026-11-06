#!/usr/bin/env python3
"""参考仓库语料量化分析（只读，标准库，可复现）。

对 .research/repos 下三个仓库的**每日产物内容本身**做统计，回答：
  - 内容分类：板块/章节是什么、出现频率多高、每板块多少条
  - 内容规范：模板采用率、字数、必备元素（链接/表格/数字/免责/参考资料）
  - 展示格式：标题层级、编号章节、引用导语、代码块、加粗、链接写法
  - 内容来源：URL 总数、域名分布、每篇来源密度

输出 reports/corpus-analysis.{json,md}。本脚本不修改任何参考仓库文件。

用法：
  python scripts/analyze_corpus.py
  python scripts/analyze_corpus.py --corpus-root <自定义路径>
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, setup_logging, LOG

URL_RE = re.compile(r"https?://[^\s)>\]\"'，。；、]+")
ARROW_LINK_RE = re.compile(r"→\s*https?://")
MD_LINK_RE = re.compile(r"\[[^\]]+\]\((https?://[^)]+)\)")
NUMBER_RE = re.compile(r"\d[\d,.]*%?")
BOLD_RE = re.compile(r"\*\*[^*]+\*\*")
CN_SECTION_RE = re.compile(r"^##\s+[一二三四五六七八九十]+、")
CN_H3_SECTION_RE = re.compile(r"^###\s+[一二三四五六七八九十]+、")
NUM_SECTION_RE = re.compile(r"^##\s+(\d+)\.?(\d+)?[\s.、]")
MONTH_RE = re.compile(r"(20\d{2})-(\d{2})")
H2_RE = re.compile(r"^##\s+(.+)$")
H3_RE = re.compile(r"^###\s+(.+)$")
LIST_RE = re.compile(r"^\s*(?:\d+\.|[-*])\s+\S")
TABLE_RE = re.compile(r"^\s*\|.*\|\s*$")
CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def files_for(corpus_root: Path, corpus: str) -> list[Path]:
    r = corpus_root / corpus
    if corpus == "daily-rss":
        return sorted(r.glob("20*/*/*.md"))
    if corpus == "daily-investor":
        return sorted((r / "observations").glob("**/*.md")) + sorted((r / "ideas").glob("*.md"))
    if corpus == "blogpost":
        return sorted(p for p in r.glob("*.md") if p.name != "README.md")
    return []


def analyze_file(path: Path) -> dict:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    lines = text.splitlines()
    urls = URL_RE.findall(text)
    domains = Counter()
    for u in urls:
        try:
            host = urlsplit(u.rstrip(".,;。")).netloc.lower()
            if host.startswith("www."):
                host = host[4:]
            if host:
                domains[host] += 1
        except ValueError:
            pass
    h2 = [m.group(1).strip() for m in (H2_RE.match(l) for l in lines) if m]
    h3 = [m.group(1).strip() for m in (H3_RE.match(l) for l in lines) if m]
    numeric_line_count = sum(1 for l in lines if NUMBER_RE.search(l))
    return {
        "path": str(path),
        "name": path.name,
        "chars": len(text),
        "lines": len(lines),
        "h1": sum(1 for l in lines if l.startswith("# ")),
        "h2": h2,
        "h2_count": len(h2),
        "h3_count": len(h3),
        "cn_numbered_sections": sum(1 for l in lines if CN_SECTION_RE.match(l)),
        "cn_numbered_h3": sum(1 for l in lines if CN_H3_SECTION_RE.match(l)),
        "num_sections": sum(1 for l in lines if NUM_SECTION_RE.match(l)),
        "blockquote_lines": sum(1 for l in lines if l.startswith(">")),
        "hr": sum(1 for l in lines if l.strip() == "---"),
        "table_rows": sum(1 for l in lines if TABLE_RE.match(l)),
        "code_fences": sum(1 for l in lines if l.strip().startswith("```")),
        "bold_spans": len(BOLD_RE.findall(text)),
        "list_items": sum(1 for l in lines if LIST_RE.match(l)),
        "arrow_links": len(ARROW_LINK_RE.findall(text)),
        "md_links": len(MD_LINK_RE.findall(text)),
        "urls": len(urls),
        "domains": domains,
        "numeric_lines": numeric_line_count,
        "numeric_line_ratio": round(numeric_line_count / max(1, len(lines)), 4),
        "cjk_chars": len(CJK_RE.findall(text)),
        "has_reference_block": bool(re.search(r"(参考资料|原文来源|数据来源|References?|原文链接)", text)),
        "has_disclaimer": bool(re.search(r"(不构成投资建议|仅供参考|免责声明|请以原文为准|自动(生成|维护))", text)),
        "has_missing_marker": "暂无可靠数据" in text,
        "has_generation_note": bool(re.search(r"(本文由|本日报由|本报告由|自动生成|生成于|翻译整理)", text)),
        "has_editor_note": bool(re.search(r"(编者观察|独立分析|一句话总结|最终结论|今日速览)", text)),
    }


def pct(n: int, total: int) -> float:
    return round(100.0 * n / max(1, total), 1)


def summarize(corpus: str, docs: list[dict], label: str) -> dict:
    total = len(docs)
    chars = [d["chars"] for d in docs]
    lines = [d["lines"] for d in docs]
    all_domains: Counter = Counter()
    h2_counter: Counter = Counter()
    month_stats: dict[str, dict] = {}
    for d in docs:
        all_domains.update(d["domains"])
        m = MONTH_RE.search(d["name"])
        if m:
            key = f"{m.group(1)}-{m.group(2)}"
            bucket = month_stats.setdefault(key, {"files": 0, "arrow": 0, "md": 0, "urls": 0})
            bucket["files"] += 1
            bucket["arrow"] += d["arrow_links"]
            bucket["md"] += d["md_links"]
            bucket["urls"] += d["urls"]
        for h in d["h2"]:
            key = re.sub(r"^\d+(\.\d+)?[\s.、]*", "", h)
            key = re.sub(r"^[一二三四五六七八九十]+、\s*", "", key)
            h2_counter[key.strip()[:40]] += 1

    def adoption(field: str) -> dict:
        n = sum(1 for d in docs if (d[field] if isinstance(d[field], bool) else d[field] > 0))
        return {"count": n, "pct": pct(n, total)}

    return {
        "corpus": corpus, "label": label, "files": total,
        "chars": {"total": sum(chars), "mean": round(statistics.mean(chars)),
                  "median": round(statistics.median(chars)), "min": min(chars), "max": max(chars)},
        "lines": {"total": sum(lines), "mean": round(statistics.mean(lines), 1),
                  "median": round(statistics.median(lines), 1), "min": min(lines), "max": max(lines)},
        "adoption": {k: adoption(k) for k in (
            "h1", "h2_count", "cn_numbered_sections", "cn_numbered_h3", "num_sections",
            "blockquote_lines",
            "hr", "table_rows", "code_fences", "bold_spans", "list_items", "arrow_links",
            "md_links", "has_reference_block", "has_disclaimer", "has_missing_marker",
            "has_generation_note", "has_editor_note")},
        "structure": {
            "h2_mean": round(statistics.mean([d["h2_count"] for d in docs]), 1),
            "h3_mean": round(statistics.mean([d["h3_count"] for d in docs]), 1),
            "list_items_mean": round(statistics.mean([d["list_items"] for d in docs]), 1),
            "bold_spans_mean": round(statistics.mean([d["bold_spans"] for d in docs]), 1),
            "urls_mean": round(statistics.mean([d["urls"] for d in docs]), 1),
            "arrow_links_mean": round(statistics.mean([d["arrow_links"] for d in docs]), 1),
            "numeric_line_ratio_mean": round(statistics.mean([d["numeric_line_ratio"] for d in docs]), 4),
            "cjk_ratio_mean": round(statistics.mean(
                [d["cjk_chars"] / max(1, d["chars"]) for d in docs]), 4),
        },
        "top_h2": [{"section": k, "files": v, "pct": pct(v, total)}
                   for k, v in h2_counter.most_common(25)],
        "urls_total": sum(d["urls"] for d in docs),
        "arrow_links_total": sum(d["arrow_links"] for d in docs),
        "md_links_total": sum(d["md_links"] for d in docs),
        "unique_domains": len(all_domains),
        "top_domains": [{"domain": k, "count": v} for k, v in all_domains.most_common(25)],
        "format_evolution_by_month": [
            {"month": k, **v,
             "arrow_per_file": round(v["arrow"] / max(1, v["files"]), 1),
             "md_per_file": round(v["md"] / max(1, v["files"]), 1)}
            for k, v in sorted(month_stats.items())],
    }


def render_markdown(result: dict) -> str:
    L = ["# 参考仓库语料量化分析报告", "",
         f"> 生成脚本：`scripts/analyze_corpus.py`（只读、标准库、可复现）",
         f"> 语料根目录：`.research/repos/`；统计口径见 `docs/12-内容规范与逆向研究.md`", ""]
    for s in result["corpora"]:
        L += [f"## {s['label']}（`{s['corpus']}`）", "",
              f"- 文件数：**{s['files']}**；总字符 {s['chars']['total']:,}；"
              f"篇幅均值 {s['chars']['mean']:,} 字符 / {s['lines']['mean']} 行，"
              f"中位 {s['chars']['median']:,} 字符；范围 {s['chars']['min']:,} ~ {s['chars']['max']:,}",
              f"- 结构均值：`##` 板块 {s['structure']['h2_mean']} 个、`###` {s['structure']['h3_mean']} 个、"
              f"列表项 {s['structure']['list_items_mean']} 条、加粗 {s['structure']['bold_spans_mean']} 处、"
              f"URL {s['structure']['urls_mean']} 个、`→ URL` {s['structure']['arrow_links_mean']} 个",
              f"- 内容密度：含数字的行占比 **{round(s['structure']['numeric_line_ratio_mean'] * 100, 1)}%**；"
              f"中文字符占比 {round(s['structure']['cjk_ratio_mean'] * 100, 1)}%",
              f"- 来源：URL 总数 {s['urls_total']:,}，唯一域名 **{s['unique_domains']:,}**，"
              f"`→ https://` 链接 {s['arrow_links_total']:,} 条，Markdown 链接 {s['md_links_total']:,} 条", "",
              "### 内容规范采用率（文件占比）", "",
              "| 元素 | 命中文件数 | 占比 |", "| --- | ---: | ---: |"]
        friendly = {"h1": "H1 标题", "h2_count": "`##` 板块",
                    "cn_numbered_sections": "中文编号章节 `## 一、`",
                    "cn_numbered_h3": "中文编号子主题 `### 一、`",
                    "num_sections": "数字编号章节（1. 2.）", "blockquote_lines": "引用导语 `>`",
                    "hr": "分隔线 `---`", "table_rows": "表格行", "code_fences": "代码围栏",
                    "bold_spans": "加粗判断句", "list_items": "列表条目",
                    "arrow_links": "`→ https://` 原文链接", "md_links": "Markdown 链接",
                    "has_reference_block": "参考资料/来源块", "has_disclaimer": "免责声明",
                    "has_missing_marker": "「暂无可靠数据」", "has_generation_note": "生成声明",
                    "has_editor_note": "编者观察/独立分析"}
        for k, label in friendly.items():
            a = s["adoption"][k]
            L.append(f"| {label} | {a['count']} | {a['pct']}% |")
        L += ["", "### 高频板块（Top 12）", "", "| 板块 | 出现文件数 | 占比 |", "| --- | ---: | ---: |"]
        for h in s["top_h2"][:12]:
            L.append(f"| {h['section']} | {h['files']} | {h['pct']}% |")
        L += ["", "### 高频来源域名（Top 12）", "", "| 域名 | 引用次数 |", "| --- | ---: |"]
        for d in s["top_domains"][:12]:
            L.append(f"| {d['domain']} | {d['count']:,} |")
        evo = s["format_evolution_by_month"]
        if evo and s["arrow_links_total"] + s["md_links_total"] > 0:
            L += ["", "### 链接写法按月演进（模板变更证据）", "",
                  "| 月份 | 文件数 | `→ URL`/篇 | Markdown 链接/篇 |", "| --- | ---: | ---: | ---: |"]
            for e in evo:
                L.append(f"| {e['month']} | {e['files']} | {e['arrow_per_file']} | {e['md_per_file']} |")
        L.append("")
    L += ["---", "", "*本报告是对产物文本的量化统计，不含生成端代码推断；逆向推理部分见 docs/12。*", ""]
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--corpus-root", default=str(ROOT / ".research" / "repos"))
    ap.add_argument("--top", type=int, default=25)
    args = ap.parse_args()
    setup_logging()

    root = Path(args.corpus_root)
    if not root.exists():
        LOG.error("语料根目录不存在：%s", root)
        return 1
    specs = [("daily-rss", "技术日报"), ("daily-investor-observations", "投资观察/美股日报"),
             ("daily-investor-ideas", "AI 产品创意日报"), ("blogpost", "深度技术文章")]
    corpora = []
    for key, label in specs:
        corpus = key.split("-observations")[0].split("-ideas")[0]
        paths = files_for(root, corpus)
        if "observations" in key:
            paths = [p for p in paths if "/observations/" in p.as_posix()]
        elif "ideas" in key:
            paths = [p for p in paths if "/ideas/" in p.as_posix()]
        if not paths:
            LOG.warning("%s 无文件，跳过", key)
            continue
        docs = [analyze_file(p) for p in paths]
        s = summarize(key, docs, label)
        s["top_h2"] = s["top_h2"][:args.top]
        s["top_domains"] = s["top_domains"][:args.top]
        corpora.append(s)
        LOG.info("%s：%d 篇，URL %d，唯一域名 %d", label, s["files"], s["urls_total"], s["unique_domains"])

    result = {"generated_by": "scripts/analyze_corpus.py", "corpus_root": str(root),
              "corpora": corpora}
    out = ROOT / "reports"
    out.mkdir(parents=True, exist_ok=True)
    # 落盘前把 Counter 转成可序列化结构
    (out / "corpus-analysis.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "corpus-analysis.md").write_text(render_markdown(result), encoding="utf-8")
    print(f"语料分析完成：{len(corpora)} 类语料 → reports/corpus-analysis.{{json,md}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
