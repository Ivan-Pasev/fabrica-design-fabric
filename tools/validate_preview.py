"""No-install validator for the public two-skill FDF review snapshot."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("fdf-motion-director", "fdf-spatial-web-architect")


def verify():
    assert (ROOT / "LICENSE").read_text("utf-8").startswith("MIT License\n"), "MIT notice missing"
    for skill in SKILLS:
        path = ROOT / "skills" / skill / "SKILL.md"
        assert path.is_file() and not path.is_symlink(), f"Missing or linked {skill}"
        text = path.read_text("utf-8")
        assert text.startswith("---\n"), f"No frontmatter: {skill}"
        front = text.split("---", 2)[1]
        assert f"name: {skill}\n" in front, f"Wrong identity: {skill}"
        assert "license: MIT\n" in front, f"License mismatch: {skill}"
        assert len(text.encode()) < 16384, f"Oversized: {skill}"
        assert any(guard in text.lower() for guard in ("read-only", "no auto imports")), f"Missing non-execution guard: {skill}"
    print("FDF public-preview contract checks PASS: 2/2 skills")
    return True


if __name__ == "__main__":
    try:
        verify()
    except (AssertionError, OSError, UnicodeError) as exc:
        print(f"HOLD: {exc}", file=sys.stderr)
        raise SystemExit(2)
