#!/usr/bin/env python3
"""GitHub Pages 本地预演：把 public/ 变成可部署副本 pages-dist/。

职责边界（P1 分发约定）：只做本地准备，绝不 git push、调用发布工具或访问网络。
默认 dry-run，--apply 才落盘；重复执行按字节幂等，内容不变则不重写。

为什么不直接推 public/：
  1. Atom / JSON Feed 的 self 与 alternate 由 build_feeds.py --base-url 写成绝对地址，
     本地默认是占位域名 https://daily-info.local，推上去就是死链。
  2. 站点前端（index.html / data/index.json）全用相对路径，天然适配
     https://<owner>.github.io/<repo>/ 子路径，所以不改这部分。
  3. tag:daily-info.local,... 是稳定 entry id，与部署域名无关；改了会让所有
     订阅阅读器把历史条目当成新条目重收，必须原样保留。
  4. 加 .nojekyll，避免 Jekyll 构建介入静态目录。
  5. 发布前独立校验：结构 / 相对链接 / XML-JSON 可解析 / 凭据 / 旧域名 / 稳定 ID。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import PUBLIC_DIR, ROOT, add_date_arg, setup_logging, LOG
from build_feeds import CREDENTIAL_PATTERNS

ATOM_NS = "{http://www.w3.org/2005/Atom}"
DEFAULT_DIST = ROOT / "pages-dist"
TEXT_SUFFIXES = {".atom", ".json", ".html", ".xml", ".txt", ".md"}


def normalize_base(url: str) -> str:
    u = (url or "").strip().rstrip("/")
    if not re.match(r"^https?://[A-Za-z0-9._:-]+(?:/[^\s]*)?$", u):
        raise ValueError("--base-url 不是合法的 http(s) 绝对地址")
    return u


def scan_credentials(blobs: dict[str, bytes]) -> list[str]:
    hits = []
    for name, data in blobs.items():
        text = data.decode("utf-8", errors="ignore")
        for pat in CREDENTIAL_PATTERNS:
            if pat.search(text):
                hits.append(name + ": " + pat.pattern)
    return hits


def build_dist(base_url: str) -> tuple[dict[str, bytes], str]:
    """在内存里构造完整部署副本，返回 (文件名字典, 旧 base_url)。"""
    if not PUBLIC_DIR.is_dir():
        raise FileNotFoundError("缺少 public/ 产物目录")
    feeds_meta = json.loads((PUBLIC_DIR / "data" / "feeds.json").read_text(encoding="utf-8"))
    old_base = str(feeds_meta.get("base_url") or "").rstrip("/")
    if not old_base:
        raise ValueError("public/data/feeds.json 缺少 base_url")

    files: dict[str, bytes] = {}
    for src in sorted(p for p in PUBLIC_DIR.rglob("*") if p.is_file()):
        if src.name.endswith(".tmp"):
            continue
        rel = src.relative_to(PUBLIC_DIR).as_posix()
        data = src.read_bytes()
        if src.suffix in TEXT_SUFFIXES:
            data = data.decode("utf-8").replace(old_base, base_url).encode("utf-8")
        files[rel] = data
    files[".nojekyll"] = b""
    return files, old_base


def validate(files: dict[str, bytes], base_url: str, old_base: str) -> list[str]:
    """独立校验部署副本。返回问题列表（空 = 通过）。"""
    problems: list[str] = []

    def text(name: str) -> str:
        return files.get(name, b"").decode("utf-8", errors="ignore")

    for name in ["index.html", "feed.atom", "feed.json", "data/index.json",
                 "data/feeds.json", "data/latest.json", ".nojekyll"]:
        if name not in files:
            problems.append("缺少必备文件 " + name)

    if old_base and old_base != base_url:
        for name, data in files.items():
            if old_base.encode("utf-8") in data:
                problems.append("旧 base_url 残留：" + name)

    html = text("index.html")
    if re.search(r"(?:href|src)\s*=\s*[\x22\x27]/(?!/)", html):
        problems.append("index.html 含根绝对路径，子路径部署会 404")
    if "daily-info.local/" in html:
        problems.append("index.html 含占位域名绝对链接")

    try:
        idx = json.loads(text("data/index.json"))
        for row in idx.get("dates", []):
            name = "data/" + row["date"] + ".json"
            if name not in files:
                problems.append("index.json 指向不存在的日期切片 " + name)
        for f in idx.get("feeds", []):
            u = str(f.get("url", ""))
            if u.startswith(("http:", "https:", "/")):
                problems.append("index.json 的 feed 链接不是相对路径：" + u)
            elif u not in files:
                problems.append("index.json 的 feed 链接无对应文件：" + u)
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        problems.append("data/index.json 解析失败：" + str(e))

    atom_files = sorted(n for n in files if n.endswith(".atom"))
    if len(atom_files) < 5:
        problems.append("Atom 文件数不足：" + str(len(atom_files)))
    for name in atom_files:
        try:
            root = ET.fromstring(files[name])
            ids = [e.text for e in root.iter(ATOM_NS + "id")]
            if not ids or not all(str(x).startswith("tag:daily-info.local,") for x in ids):
                problems.append(name + " 的稳定 ID 被改写或缺失")
            # 只取 feed 级 link；entry 内的 alternate 指向外部原文，不该改成本站域名
            links = {e.get("rel"): e.get("href") for e in root.findall(ATOM_NS + "link")}
            for rel in ("self", "alternate"):
                if not str(links.get(rel, "")).startswith(base_url):
                    problems.append(name + " rel=" + rel + " 未指向新域名")
        except ET.ParseError as e:
            problems.append(name + " XML 解析失败：" + str(e))

    try:
        jf = json.loads(text("feed.json"))
        for key in ("home_page_url", "feed_url"):
            if not str(jf.get(key, "")).startswith(base_url):
                problems.append("feed.json 的 " + key + " 未指向新域名")
    except json.JSONDecodeError as e:
        problems.append("feed.json 解析失败：" + str(e))

    try:
        fm = json.loads(text("data/feeds.json"))
        if fm.get("base_url") != base_url:
            problems.append("data/feeds.json base_url 未更新")
        for p in fm.get("profiles", []):
            if not str(p.get("url", "")).startswith(base_url):
                problems.append("data/feeds.json profile 未更新：" + str(p.get("id")))
    except json.JSONDecodeError as e:
        problems.append("data/feeds.json 解析失败：" + str(e))

    for name in (n for n in files if n.endswith(".json")):
        try:
            json.loads(files[name].decode("utf-8"))
        except json.JSONDecodeError as e:
            problems.append(name + " JSON 解析失败：" + str(e))

    problems.extend("凭据特征命中：" + h for h in scan_credentials(files))
    return problems


def write_dist(files: dict[str, bytes], dist: Path) -> tuple[int, int, list[str]]:
    """字节幂等写入；返回 (新增/更新数, 未变化数, 陈旧文件列表)。"""
    dist.mkdir(parents=True, exist_ok=True)
    changed = same = 0
    for name, data in sorted(files.items()):
        dst = dist / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists() and dst.read_bytes() == data:
            same += 1
            continue
        dst.write_bytes(data)
        changed += 1
    expected = set(files)
    stale = sorted(p.relative_to(dist).as_posix() for p in dist.rglob("*")
                   if p.is_file() and p.relative_to(dist).as_posix() not in expected
                   and p.name != "manifest.json")
    return changed, same, stale


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    add_date_arg(ap)
    ap.add_argument("--base-url", required=True,
                    help="Pages 公开地址，如 https://<owner>.github.io/<repo>")
    ap.add_argument("--dist-dir", default=str(DEFAULT_DIST))
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    setup_logging(args.verbose)

    try:
        base_url = normalize_base(args.base_url)
        files, old_base = build_dist(base_url)
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as e:
        LOG.error("构造部署副本失败：%s", e)
        return 2

    problems = validate(files, base_url, old_base)
    total_bytes = sum(len(v) for v in files.values())
    manifest = {
        "base_url": base_url,
        "replaced_from": old_base,
        "file_count": len(files),
        "total_bytes": total_bytes,
        "generated_by": "prepare_pages.py (local only, no network / no push)",
        "files": [{"name": n, "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()}
                  for n, b in sorted(files.items())],
    }
    files["manifest.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")

    LOG.info("base_url: %s -> %s", old_base, base_url)
    LOG.info("文件 %d 个 / %d bytes；稳定 ID 保留", len(files), total_bytes)
    for p in problems:
        LOG.error("校验不通过：%s", p)
    if problems:
        LOG.error("共 %d 项问题，拒绝生成部署副本", len(problems))
        return 1

    if not args.apply:
        LOG.info("dry-run 通过（0 项问题）：加 --apply 生成 %s", args.dist_dir)
        print("")
        print("部署副本计划（前 12 项）：")
        for row in manifest["files"][:12]:
            print("  %-32s %8d B  %s" % (row["name"], row["bytes"], row["sha256"][:12]))
        print("  ... 共 %d 项，合计 %d B" % (manifest["file_count"], total_bytes))
        return 0

    changed, same, stale = write_dist(files, Path(args.dist_dir))
    LOG.info("写入完成：changed=%d no_change=%d stale=%d", changed, same, len(stale))
    for name in stale:
        LOG.warning("陈旧文件（未自动删除，请人工确认）：%s", name)
    print("[pages] base_url=%s files=%d changed=%d no_change=%d stale=%d -> %s" %
          (base_url, len(files), changed, same, len(stale), args.dist_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())