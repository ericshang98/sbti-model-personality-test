"""
Extract SBTI questions, dimensions, patterns, and type descriptions from the
original index.html (by @蛆肉儿串儿, repo: UnluckyNinja/SBTI-test) into clean JSON.

Run once after cloning the original repo:
    git clone https://github.com/UnluckyNinja/SBTI-test.git
    python extract_from_source.py path/to/SBTI-test/index.html
"""
import json
import re
import sys
from pathlib import Path


def extract_js_object(html: str, var_name: str) -> str:
    """Grab the text of a JS object/array literal assigned to `var_name`."""
    start_re = re.compile(rf"const\s+{re.escape(var_name)}\s*=\s*")
    m = start_re.search(html)
    if not m:
        raise RuntimeError(f"Could not find `const {var_name} =` in html")
    i = m.end()
    # find opening bracket
    while html[i] not in "[{":
        i += 1
    open_ch = html[i]
    close_ch = "]" if open_ch == "[" else "}"
    depth = 0
    in_str = False
    str_ch = ""
    escape = False
    j = i
    while j < len(html):
        c = html[j]
        if in_str:
            if escape:
                escape = False
            elif c == "\\":
                escape = True
            elif c == str_ch:
                in_str = False
        else:
            if c in ("'", '"', "`"):
                in_str = True
                str_ch = c
            elif c == open_ch:
                depth += 1
            elif c == close_ch:
                depth -= 1
                if depth == 0:
                    return html[i : j + 1]
        j += 1
    raise RuntimeError(f"Unbalanced brackets while extracting {var_name}")


def js_literal_to_json(js: str) -> str:
    """Convert a JS object literal to JSON (handles unquoted keys & single quotes)."""
    # Quote unquoted object keys:  foo:  -> "foo":
    out = re.sub(r"([{,]\s*)([A-Za-z_$][\w$!-]*)\s*:", r'\1"\2":', js)
    # Convert single-quoted strings to JSON double-quoted, preserving inner "
    def repl_sq(match: re.Match) -> str:
        inner = match.group(1)
        inner = inner.replace('\\"', '"').replace('"', '\\"').replace("\\'", "'")
        return '"' + inner + '"'

    out = re.sub(r"'((?:\\.|[^'\\])*)'", repl_sq, out)
    # Remove trailing commas before } or ]
    out = re.sub(r",(\s*[}\]])", r"\1", out)
    return out


def main() -> None:
    if len(sys.argv) != 2:
        print("usage: extract_from_source.py path/to/SBTI-test/index.html")
        sys.exit(1)
    html = Path(sys.argv[1]).read_text(encoding="utf-8")

    out_dir = Path(__file__).parent / "data"
    out_dir.mkdir(exist_ok=True)

    specs = [
        ("questions", "questions.json"),
        ("specialQuestions", "special_questions.json"),
        ("dimensionMeta", "dimensions.json"),
        ("NORMAL_TYPES", "patterns.json"),
        ("TYPE_LIBRARY", "types.json"),
        ("DIM_EXPLANATIONS", "dim_explanations.json"),
    ]
    for var, filename in specs:
        raw = extract_js_object(html, var)
        # Some blocks (TYPE_LIBRARY, DIM_EXPLANATIONS) are already JSON-compatible
        # (double-quoted keys + strings). Try direct parse first, fall back to
        # js-literal conversion for the rest.
        cleaned = re.sub(r",(\s*[}\]])", r"\1", raw)
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            data = json.loads(js_literal_to_json(raw))
        (out_dir / filename).write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        if isinstance(data, list):
            print(f"  {filename}: {len(data)} items")
        else:
            print(f"  {filename}: {len(data)} keys")


if __name__ == "__main__":
    main()
