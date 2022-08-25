from __future__ import annotations

from pathlib import Path
from typing import Dict, List
from pydantic import BaseModel


class IlliterateConfig(BaseModel):
    inline: bool = False
    title: bool = False
    linenums: bool = False
    highlights: bool = False
    sources: Dict[str, str]

    def expanded(self) -> IlliterateConfig:
        expanded_sources = {}
        cwd = Path.cwd()
        prefix_len = len(str(cwd))

        for input_pattern, output_pattern in self.sources.items():
            if Path(input_pattern).is_dir():
                input_paths = Path(input_pattern).resolve().rglob("*.py")
            else:
                input_paths = Path.cwd().rglob(input_pattern)

            for input_path in input_paths:
                input_str = str(input_path)[prefix_len + 1 :]
                output_str = output_pattern.replace("*", input_path.stem)

                if Path(output_str).is_dir():
                    output_str = Path(output_str) / input_str

                    if input_path.suffix == ".py":
                        output_str = output_str.with_suffix(".md")

                expanded_sources[input_str] = str(output_str)

        return IlliterateConfig(inline=self.inline, sources=expanded_sources)

    @classmethod
    def make(cls, *, sources: List[str], **kwargs):
        source_dict = {}

        for line in sources:
            input, output = line.split(":")
            source_dict[input] = output

        return cls(sources=source_dict, **kwargs)

    def files(self):
        for input_path, output_path in self.expanded().sources.items():
            yield Path(input_path).resolve(), Path(output_path).resolve()
