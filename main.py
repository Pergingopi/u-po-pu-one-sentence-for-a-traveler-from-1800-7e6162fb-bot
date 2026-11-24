"""One sentence for a traveler from 1800.

Writes a single sentence (at most 200 characters) explaining the modern
internet to someone arriving from the year 1800, using only words a person
from 1800 would know: a road, a post office, a library, a market, a letter,
a picture, a voice, ink. The output goes to $MAKEFUN_OUTPUT_DIR/entry.txt
(default /output; an empty value falls back to /output), with no trailing
newline, so the file holds exactly the sentence the gate counts.
"""

import os
import sys
import tempfile

SENTENCE = (
    "Picture one road of light joining every library, post office, and "
    "market on earth, so any letter, picture, or voice reaches the far "
    "side of the world before your ink dries."
)


def _validate(text: str) -> None:
    if not 1 <= len(text) <= 200:
        raise SystemExit(f"sentence must be 1-200 characters, got {len(text)}")
    if text != text.strip() or text != " ".join(text.split()):
        raise SystemExit("sentence must have no leading/trailing/double space")
    if any(ord(ch) < 0x20 or ord(ch) == 0x7F for ch in text):
        raise SystemExit("sentence must not contain control characters")
    if text.count(".") != 1 or not text.endswith("."):
        raise SystemExit("entry must be exactly one sentence")
    if "\n" in text:
        raise SystemExit("entry must not contain a newline")


def _fsync_dir(path: str) -> None:
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def main() -> None:
    _validate(SENTENCE)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.txt")
    fd, tmp = tempfile.mkstemp(dir=out_dir, prefix=".entry-", suffix=".tmp")
    try:
        os.chmod(tmp, 0o644)
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(SENTENCE)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp, 0o644)
        os.replace(tmp, target)
        os.chmod(target, 0o644)
        _fsync_dir(out_dir)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    with open(target, "r", encoding="utf-8", newline="") as f:
        written = f.read()
    if written != SENTENCE:
        raise SystemExit("read-back mismatch")
    sys.stdout.write(f"wrote {target} ({len(SENTENCE)} characters)\n")


if __name__ == "__main__":
    main()
