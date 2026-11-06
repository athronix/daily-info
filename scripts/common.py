#!/usr/bin/env python3
"""共享工具：路径、配置、时间、URL 规范化、通用 RSS/Atom 解析、JSONL、运行日志。

设计原则：只依赖 Python 标准库，保证在 WorkBuddy 定时任务里零安装即可运行。
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import logging
import os
import re
import sys
import zlib
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config"
DATA_DIR = ROOT / "data"
PUBLIC_DIR = ROOT / "public"
LOG = logging.getLogger("daily-info")

TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "fbclid", "gclid", "dclid", "msclkid", "igshid", "spm", "ref", "ref_src",
    "source", "mc_cid", "mc_eid", "_hsenc", "mkt_tok",
}


def setup_logging(verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stdout,
    )


def load_config(name: str) -> dict:
    path = CONFIG_DIR / name
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def today_str(tz_offset_hours: int = 8) -> str:
    return (now_utc() + timedelta(hours=tz_offset_hours)).date().isoformat()


def day_dir(layer: str, date: str) -> Path:
    p = DATA_DIR / layer / date
    p.mkdir(parents=True, exist_ok=True)
    return p


def write_json(path: Path, obj) -> bool:
    """幂等写入：内容未变则不落盘，返回是否发生写入。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)
    return True


def write_bytes_idempotent(path: Path, data: bytes) -> bool:
    """幂等写字节：内容未变则不落盘，返回是否发生写入（供分发 payload / CSV / HTML 复用）。

    按字节而非按解码文本比对，避免 utf-8-sig 等带 BOM 编码在往返解码时误判为「有变更」。
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() == data:
        return False
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(data)
    tmp.replace(path)
    return True


def write_text_idempotent(path: Path, content: str, encoding: str = "utf-8") -> bool:
    return write_bytes_idempotent(path, content.encode(encoding))


def read_json(path: Path, default=None):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def append_jsonl(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def canonical_url(url: str) -> str:
    if not url:
        return ""
    try:
        parts = urlsplit(url.strip())
        query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
                 if k.lower() not in TRACKING_PARAMS]
        path = parts.path.rstrip("/") or "/"
        clean = urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path,
                            urlencode(query), ""))
        return clean
    except ValueError:
        return url.strip()


def item_id(url: str, guid: str = "") -> str:
    base = canonical_url(url) or guid
    return hashlib.sha1(base.encode("utf-8")).hexdigest()[:16]


def parse_when(value: str | None) -> str | None:
    """尽力把各种 feed 时间字符串转成 UTC ISO8601（Z 结尾）。"""
    if not value:
        return None
    value = value.strip()
    try:
        if value.endswith("Z") or re.search(r"[+-]\d{2}:?\d{2}$", value):
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        else:
            dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    except ValueError:
        pass
    try:
        dt = parsedate_to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    except (TypeError, ValueError, IndexError):
        return None


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data):
        self.parts.append(data)

    def text(self) -> str:
        return " ".join("".join(self.parts).split())


def strip_html(raw: str | None, limit: int = 2000) -> str:
    if not raw:
        return ""
    p = _TextExtractor()
    try:
        p.feed(raw)
        p.close()
        return p.text()[:limit]
    except Exception:
        return html.unescape(re.sub(r"<[^>]+>", " ", raw))[:limit]


def _child_text(node: ET.Element, names: tuple[str, ...]) -> str:
    for child in node:
        tag = child.tag.rsplit("}", 1)[-1].lower()
        if tag in names:
            if tag in ("link",) and not (child.text or "").strip():
                return child.attrib.get("href", "")
            return "".join(child.itertext()).strip()
    return ""


def decode_payload(payload: bytes, headers=None) -> bytes:
    """解压 HTTP 响应体。

    实测坑：deepmind.google/blog/rss.xml 返回 200 + Content-Type: application/xml，
    但响应体其实是 gzip 且**未设置 Content-Encoding**（2026-11-05），urllib 不会自动解压，
    parse_feed 直接 ParseError。因此这里按魔数兜底，不依赖服务端声明。
    用 zlib.decompressobj 而非 gzip.decompress，是为了让 check_sources 只读 4KB 样本时
    也能解出开头（截断的 gzip 流不会抛 EOFError）。
    """
    enc = ((headers.get("Content-Encoding") if headers else "") or "").lower()
    if payload[:2] == b"\x1f\x8b" or "gzip" in enc:
        try:
            return zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(payload)
        except zlib.error:
            return payload
    if "deflate" in enc:
        for wbits in (zlib.MAX_WBITS, -zlib.MAX_WBITS):
            try:
                return zlib.decompress(payload, wbits)
            except zlib.error:
                continue
    return payload


def parse_feed(payload: bytes) -> list[dict]:
    """同时兼容 RSS 2.0 与 Atom 1.0；返回未归一化的原始条目。"""
    try:
        root = ET.fromstring(payload)
    except ET.ParseError:
        # 容错：去掉 XML 1.0 非法控制字符后重试
        cleaned = re.sub(rb"[\x00-\x08\x0b\x0c\x0e-\x1f]", b"", payload)
        root = ET.fromstring(cleaned)
    tag = root.tag.rsplit("}", 1)[-1].lower()
    out: list[dict] = []
    if tag == "rss" or root.findall(".//{*}item"):
        for node in root.iter():
            if node.tag.rsplit("}", 1)[-1].lower() != "item":
                continue
            out.append({
                "guid": _child_text(node, ("guid", "id")),
                "title": strip_html(_child_text(node, ("title",)), 400),
                "url": _child_text(node, ("link",)) or _child_text(node, ("guid",)),
                "summary": strip_html(_child_text(node, ("description", "summary", "encoded")), 2000),
                "published_raw": _child_text(node, ("pubdate", "published", "date", "dc:date")),
                "author": _child_text(node, ("author", "creator")),
            })
    else:
        ns = "{http://www.w3.org/2005/Atom}"
        for node in root.findall(f"{ns}entry") or [e for e in root.iter() if e.tag.endswith("}entry")]:
            link = ""
            for child in node:
                t = child.tag.rsplit("}", 1)[-1].lower()
                if t == "link" and (child.attrib.get("rel") in (None, "alternate")):
                    link = child.attrib.get("href", "")
                    break
            out.append({
                "guid": _child_text(node, ("id",)),
                "title": strip_html(_child_text(node, ("title",)), 400),
                "url": link or _child_text(node, ("id",)),
                "summary": strip_html(_child_text(node, ("summary", "content")), 2000),
                "published_raw": _child_text(node, ("published", "updated")),
                "author": _child_text(node, ("name",)),
            })
    return [o for o in out if o.get("title") or o.get("url")]


def _openalex_abstract(work: dict) -> str:
    """OpenAlex 摘要以 inverted index（词 -> 位置列表）返回，按位置重排成文本。"""
    inv = work.get("abstract_inverted_index") or {}
    pos: dict[int, str] = {}
    for term, idxs in inv.items():
        for i in idxs:
            pos[i] = term
    return " ".join(pos[i] for i in sorted(pos))


def json_api_items(payload: bytes, source: dict) -> list[dict]:
    """把常见 JSON API 响应映射成与 RSS 相同的原始条目结构。"""
    data = json.loads(payload.decode("utf-8", "replace"))
    sid = source["id"]
    out: list[dict] = []
    if sid == "hn-algolia":
        for hit in data.get("hits", []):
            out.append({
                "guid": str(hit.get("objectID", "")),
                "title": hit.get("title") or hit.get("story_title") or "",
                "url": hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                "summary": strip_html(hit.get("story_text") or ""),
                "published_raw": hit.get("created_at"),
                "metrics": {"hn_points": hit.get("points") or 0,
                            "comments": hit.get("num_comments") or 0},
            })
    elif sid in ("gh-search-new-repos", "gh-search-topic-mcp"):
        for repo in data.get("items", []):
            out.append({
                "guid": f"github:{repo.get('id')}",
                "title": f"{repo.get('full_name')} · ★{repo.get('stargazers_count')}",
                "url": repo.get("html_url", ""),
                "summary": repo.get("description") or "",
                "published_raw": repo.get("created_at"),
                "metrics": {"github_stars": repo.get("stargazers_count") or 0},
            })
    elif sid == "openalex":
        for w in data.get("results", []):
            doi = (w.get("doi") or "").replace("https://doi.org/", "")
            url = f"https://doi.org/{doi}" if doi else (w.get("landing_page_url") or "")
            out.append({
                "guid": f"openalex:{w.get('id', '').rsplit('/', 1)[-1]}",
                "title": (w.get("title") or "")[:300],
                "url": url,
                "summary": _openalex_abstract(w)[:600],
                "published_raw": w.get("published_time") or w.get("created_time"),
                "metrics": {"cited_by_count": w.get("cited_by_count") or 0},
            })
    elif sid == "hf-daily-papers":
        papers = data if isinstance(data, list) else data.get("papers", [])
        for p in papers[:40]:
            paper = p.get("paper", p)
            pid = paper.get("id", "")
            out.append({
                "guid": f"hfpaper:{pid}",
                "title": paper.get("title", "").strip(),
                "url": f"https://huggingface.co/papers/{pid}",
                "summary": (paper.get("summary") or "")[:600],
                "published_raw": p.get("publishedAt") or paper.get("publishedAt"),
                "metrics": {"upvotes": paper.get("upvotes") or 0},
            })
    elif sid == "sec-submissions-returns":
        for rec in (data.get("filings", {}) or {}).get("recent", {}).get("accessionNumber", [])[:25]:
            idx = (data.get("filings", {}) or {}).get("recent", {}).get("accessionNumber", []).index(rec)
            forms = data["filings"]["recent"].get("form", [])
            if idx >= len(forms) or not str(forms[idx]).startswith(("8-K", "10-Q", "10-K")):
                continue
            out.append({
                "guid": rec,
                "title": f"{data.get('name', 'Apple')} 提交 {forms[idx]}（{rec}）",
                "url": f"https://www.sec.gov/Archives/edgar/data/{data.get('cik', '')}/{rec.replace('-', '')}/",
                "summary": f"SEC EDGAR filing {forms[idx]}",
                "published_raw": data["filings"]["recent"].get("filingDate", [""])[idx],
                "metrics": {},
            })
    elif sid == "yahoo-chart":
        result = (data.get("chart") or {}).get("result") or [{}]
        meta = result[0].get("meta", {}) if result else {}
        out.append({
            "guid": f"yahoo:{meta.get('symbol')}:{meta.get('regularMarketTime')}",
            "title": f"{meta.get('symbol')} 收盘 {meta.get('regularMarketPrice')}",
            "url": f"https://finance.yahoo.com/quote/{meta.get('symbol')}",
            "summary": f"previousClose={meta.get('previousClose')} currency={meta.get('currency')}",
            "published_raw": None,
            "metrics": {"price": meta.get("regularMarketPrice")},
        })
    elif sid == "baai-hub":
        # 智源社区：匿名 POST /api/v1/story/list，响应 data[].story_info。
        # 首页 __NUXT__ 也内嵌同样的 6 条，但 API 可翻页、字段规整，故以 API 为主。
        for row in (data.get("data") or []):
            info = row.get("story_info") or row
            title = (info.get("title") or "").strip()
            if not title:
                continue
            created = (info.get("created_at") or "").replace(" 分享", "").strip()
            if re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", created):
                created = created.replace(" ", "T") + ":00+08:00"
            tags = "、".join(t.get("title", "") for t in (info.get("tag_names") or [])
                            if isinstance(t, dict) and t.get("title"))
            summary = strip_html(info.get("summary") or info.get("content") or "")[:600]
            out.append({
                "guid": f"baai:{info.get('id')}",
                "title": title,
                "url": info.get("url") or "https://hub.baai.ac.cn/",
                "summary": (tags + "｜" + summary) if tags else summary,
                "published_raw": created,
                "author": info.get("user_name") or "智源社区",
                "metrics": {},
            })
    elif sid == "hf-spaces-new":
        # Hugging Face Spaces 新建列表：顶层数组，无 summary 字段，用 tags/cardData 兜底。
        spaces = data if isinstance(data, list) else (data.get("spaces") or data.get("items") or [])
        for sp in spaces[:30]:
            sid_ = sp.get("id") or sp.get("_id") or ""
            if not sid_:
                continue
            card = sp.get("cardData") or {}
            summary = (card.get("short_description")
                       or "、".join(sp.get("tags") or [])
                       or f"Hugging Face Space {sid_}")
            out.append({
                "guid": f"hfspace:{sid_}",
                "title": f"{sid_} · HF Space",
                "url": f"https://huggingface.co/spaces/{sid_}",
                "summary": str(summary)[:500],
                "published_raw": sp.get("createdAt"),
                "metrics": {"likes": sp.get("likes") or 0},
            })
    else:
        raise ValueError(f"未实现的 json_api 源: {sid}")
    return out


def parse_html_items(payload: bytes, source: dict) -> list[dict]:
    """Tier C 源的最小可用 HTML 解析；解析不出即返回空列表并由上层整源降级。"""
    text = payload.decode("utf-8", "replace")
    sid = source["id"]
    out: list[dict] = []
    if sid == "github-trending":
        pattern = re.compile(r'<h2[^>]*class="[^"]*h3[^"]*"[^>]*>\s*<a[^>]*href="(/[^"]+)"', re.S)
        for m in pattern.finditer(text):
            out.append({"guid": m.group(1), "title": m.group(1).strip("/").replace("/", " / "),
                        "url": "https://github.com" + m.group(1), "summary": "",
                        "published_raw": None})
    elif sid == "anthropic-news":
        pattern = re.compile(r'<a[^>]+href="(/news/[^"]+)"[^>]*>(.*?)</a>', re.S)
        for m in pattern.finditer(text):
            title = strip_html(m.group(2), 200)
            if title:
                out.append({"guid": m.group(1), "title": title,
                            "url": "https://www.anthropic.com" + m.group(1),
                            "summary": "", "published_raw": None})
    elif sid == "aigc-link":
        # AIGCLINK 是 Notion SPA，首屏 HTML 无内容。这里接 r.jina.ai 的 Markdown 渲染结果：
        # [![Image N](cover) 标题 YYYY/MM/DD 标签… 摘要](https://d.aigclink.ai/<slug>?pvs=25)
        # 每条自带日期、标签、摘要与站内原文链接，正好满足「实在、具体」的内容契约。
        link_re = re.compile(
            r"\[!\[Image\s+\d+\]\([^)]*\)\s*(.*?)\]\((https://d\.aigclink\.ai/[^)\s]+)\)",
            re.S,
        )
        date_re = re.compile(r"\b(20\d{2}/\d{2}/\d{2})\b")
        for m in link_re.finditer(text):
            content = " ".join(m.group(1).split())
            dm = date_re.search(content)
            if not dm:
                continue
            title = content[:dm.start()].strip()
            if not title:
                continue
            out.append({
                "guid": m.group(2).split("?")[0],
                "title": title[:300],
                "url": m.group(2),
                "summary": content[dm.end():].strip()[:800],
                "published_raw": dm.group(1).replace("/", "-") + "T00:00:00Z",
                "author": "AIGCLINK",
            })
    else:
        parser = source.get("parser")
        raise ValueError(f"未实现的 HTML 解析器: {parser or sid}")
    return out[:30]


CREDENTIAL_PLACEHOLDER = re.compile(r"\$\{([A-Z][A-Z0-9_]*)\}")
_DOTENV_LOADED = False


def load_dotenv() -> int:
    """把 ~/.workbuddy/.env 的 KEY=VALUE 注入 os.environ（不覆盖已有值）。

    实测背景（2026-11-05）：WorkBuddy 的 `C:/Users/towyq/.workbuddy/.env` **不会**自动进入
    子进程环境（GITHUB_TOKEN / USER / EMAIL 在 os.environ 里全是 MISSING），
    所以采集链必须自己加载，否则 `${VAR}` 占位永远解析不到、一直回退匿名。

    优先级：`PERSONAL_DAILY_INFO_DOTENV` 指定路径 → `~/.workbuddy/.env` → `ROOT/.env`。
    只读第一个存在的文件；全程不打印、不落盘、不返回任何值（只返回注入的键数量）。
    """
    global _DOTENV_LOADED
    if _DOTENV_LOADED:
        return 0
    _DOTENV_LOADED = True
    paths: list[Path] = []
    override = os.environ.get("PERSONAL_DAILY_INFO_DOTENV")
    if override:
        paths.append(Path(override))
    paths += [Path.home() / ".workbuddy" / ".env", ROOT / ".env"]
    count = 0
    for path in paths:
        if not path.is_file():
            continue
        try:
            lines = path.read_text(encoding="utf-8-sig").splitlines()
        except OSError:
            continue
        for line in lines:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            if s.startswith("export "):
                s = s[7:].strip()
            if "=" not in s:
                continue
            key, val = s.split("=", 1)
            key, val = key.strip(), val.strip()
            if len(val) >= 2 and val[0] == val[-1] and val[0] in ("'", '"'):
                val = val[1:-1]
            if (re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key)
                    and key not in os.environ and val):
                os.environ[key] = val
                count += 1
        break  # 只读第一个存在的文件，避免多份配置互相覆盖
    return count


def redact_credentials(text: str, source: dict) -> str:
    """把已注入的凭据/邮箱值还原成 ${VAR} 占位，供日志、异常与报告使用。

    用于 `final_url`、HTTP 异常文本等会进入 `reports/` 的字段：
    OpenAlex 的 `mailto=<真实邮箱>`、GitHub 的 token 都不应写进健康报告。
    """
    if not text:
        return text
    load_dotenv()
    declared = set(CREDENTIAL_PLACEHOLDER.findall(json.dumps(source, ensure_ascii=False)))
    for var in declared:
        val = os.environ.get(var)
        if val and len(val) >= 3 and val in text:
            text = text.replace(val, "${" + var + "}")
    return text


def resolve_credentials(source: dict) -> dict:
    """把 ${ENV_VAR} 占位替换为进程环境变量值；密钥永不写入仓库文件。

    约定（配合 docs/03「不存储任何 API Key / token 在仓库」）：
      - header 值里含未设置的占位 → 整个 header 丢弃，该源自动回退匿名模式；
      - URL / body 里的占位 → 替换为空串，因此只允许放非密钥参数（如 OpenAlex mailto）；
      - 返回深拷贝；原始 source 保持不变，落盘记录保留带占位的 URL（天然脱敏）。
    这样「用户提供 token 就提额，不提供也照常跑」，不会出现半配置状态。
    """
    load_dotenv()
    out = json.loads(json.dumps(source))
    hdr = out.get("headers") or {}
    for key, val in list(hdr.items()):
        if not isinstance(val, str):
            continue
        matches = list(CREDENTIAL_PLACEHOLDER.finditer(val))
        if not matches:
            continue
        if any(not os.environ.get(m.group(1)) for m in matches):
            hdr.pop(key, None)
        else:
            hdr[key] = CREDENTIAL_PLACEHOLDER.sub(
                lambda m: os.environ[m.group(1)], val)
    if isinstance(out.get("url"), str):
        out["url"] = CREDENTIAL_PLACEHOLDER.sub(
            lambda m: os.environ.get(m.group(1), ""), out["url"])

    def _sub(obj):
        if isinstance(obj, str):
            return CREDENTIAL_PLACEHOLDER.sub(
                lambda m: os.environ.get(m.group(1), ""), obj)
        if isinstance(obj, dict):
            return {k: _sub(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_sub(v) for v in obj]
        return obj

    if isinstance(out.get("body"), dict):
        out["body"] = _sub(out["body"])
    return out


def run_log(event: str, **fields) -> None:
    append_jsonl(DATA_DIR / "state" / "run-log.jsonl",
                 {"ts": now_utc().isoformat().replace("+00:00", "Z"),
                  "event": event, **fields})


def add_date_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--date", default=today_str(), help="业务日期 YYYY-MM-DD，默认北京时间今天")
    parser.add_argument("--root", default=str(ROOT), help="项目根目录（便于在工作区外试跑）")
    parser.add_argument("-v", "--verbose", action="store_true")
