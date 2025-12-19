"""
CLI entry point for OmegaParser.

Usage:
    omegaparser input.zip --out ./output
    omegaparser /path/to/directory --out ./output
"""

import argparse
import sys
from pathlib import Path

from .main import OmegaParser


def main():
    parser = argparse.ArgumentParser(
        prog="omegaparser",
        description="OmegaParser — The last parser you'll ever need.",
        epilog="Example: omegaparser input.zip --out ./output"
    )

    parser.add_argument(
        "input",
        help="Path to ZIP file or directory to parse"
    )
    
    parser.add_argument(
        "--out",
        required=True,
        help="Output directory for parsed data"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="omegaparser v0.1.0"
    )

    args = parser.parse_args()

    # Validate input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input path does not exist: {args.input}", file=sys.stderr)
        sys.exit(1)
    
    # Run parser
    try:
        omegaparser = OmegaParser(verbose=args.verbose)
        omegaparser.parse(args.input, args.out)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
