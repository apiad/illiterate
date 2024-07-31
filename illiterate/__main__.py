import argparse
from . import Tangle


parser = argparse.ArgumentParser("illiterate")
parser.add_argument("src_path")
parser.add_argument("dst_path")
parser.add_argument("--formats", nargs="*", default=["md", "qmd", "txt"])
parser.add_argument("--delimiter", default="```")
parser.add_argument("--directives", default="#:")


if __name__ == "__main__":
    args = parser.parse_args()
    tangle = Tangle(
        args.src_path,
        args.dst_path,
        formats=args.formats,
        delimiter=args.delimiter,
        directives=args.directives,
    )

    tangle.tangle()