"""One-time avatar preprocessing for DH_live digital human.

Usage:
    python scripts/preprocess_avatar.py --input <avatar_video.mp4> --output <avatar_data_dir>

If --output is omitted, uses the default avatar data directory.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_AGENT_ROOT = Path(__file__).resolve().parent.parent
if str(_AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(_AGENT_ROOT))


def main() -> None:
    parser = argparse.ArgumentParser(description="Preprocess avatar video for DH_live")
    parser.add_argument(
        "--input",
        required=True,
        type=str,
        help="Path to silent avatar video (MP4, single person, front-facing).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output directory for avatar data. Defaults to dh_live/avatar_data.",
    )
    args = parser.parse_args()

    from src.ai_modules.generation.video_renderer import VideoRendererService

    renderer = VideoRendererService()
    output_dir = renderer.preprocess_avatar(
        video_path=Path(args.input),
        output_dir=Path(args.output) if args.output else None,
    )
    print(f"Avatar data generated at: {output_dir}")
    print(f"  Assets: {output_dir / 'assets' / 'combined_data.json.gz'}")
    print(f"  Avatar video: {output_dir / '01.mp4'}")


if __name__ == "__main__":
    main()
