from pathlib import Path
import collections
import re


MACRO_RE = re.compile(r"<<<\s(?P<id>[\w\-_]+)\s>>>")


class Chunk:
    def __init__(self, content, *, id=None, source=None, **kwargs) -> None:
        if id is None and source is None:
            raise ValueError("Exaclty one of id or source must be defined.")

        if id is not None and source is not None:
            raise ValueError("Exactly one of id or source must be defined.")

        self.content = content
        self.id = id
        self.source = source
        self.references = MACRO_RE.findall(self.content)

    def __repr__(self) -> str:
        return f"Chunk({repr(self.content)}, id={repr(self.id)}, source={repr(self.source)}, references={repr(self.references)})"

    def __str__(self) -> str:
        return self.content

    def resolve(self, by_id: dict[str, "Chunk"]) -> str:
        content = self.content

        for id in self.references:
            content = content.replace(f"<<< {id} >>>", by_id[id].resolve(by_id))

        return content

    @classmethod
    def from_lines(cls, lines: list[str], directives: str):
        content = []
        args = {}

        for line in lines:
            if line.startswith(directives):
                arg, value = line[len(directives) :].strip().split("=")
                args[arg] = value
            else:
                if line.strip():
                    content.append(line)

        return cls("".join(content).strip("\n"), **args)


class ChunkGraph:
    def __init__(self, chunks: list[Chunk]) -> None:
        self.chunks = chunks
        self.by_id = {chunk.id: chunk for chunk in chunks if chunk.id is not None}
        self.by_source: dict[str, list[Chunk]] = collections.defaultdict(list)

        for chunk in chunks:
            if chunk.source is not None:
                self.by_source[chunk.source].append(chunk)

    def sort(self):
        for src in self.by_source:
            yield src, [chunk.resolve(self.by_id) for chunk in self.by_source[src]]


class Tangle:
    def __init__(
        self,
        src_path: str | Path,
        dst_path: str | Path,
        *,
        formats: list[str] = None,
        delimiter="```",
        directives="#:",
    ) -> None:
        self.src_path = Path(src_path)
        self.dst_path = Path(dst_path)
        self.formats = formats or ["md", "qmd", "txt"]
        self.delimiter = delimiter
        self.directives = directives

    def tangle(self):
        chunks = self._collect()
        graph = ChunkGraph(chunks)

        for src, chunks in graph.sort():
            with open(self.dst_path / src, "w") as fp:
                for chunk in chunks:
                    fp.write(chunk)
                    fp.write("\n\n")

    def _collect(self) -> list[Chunk]:
        files: list[Path] = []

        for format in self.formats:
            files.extend(self.src_path.rglob(f"*.{format}"))

        chunks: list[Chunk] = []

        for file in files:
            with file.open() as fp:
                chunks.extend(self._parse(fp.readlines()))

        return chunks

    def _parse(self, content: list[str]) -> list[Chunk]:
        state = "text"
        chunk = []
        chunks: list[Chunk] = []

        for line in content:
            if line.startswith(self.delimiter):
                if state == "text":
                    state = "code"
                else:
                    chunks.append(Chunk.from_lines(chunk, self.directives))
                    chunk = []
                    state = "text"
                continue

            if state == "code":
                chunk.append(line)

        if chunk:
            raise ValueError("Unfinished chunk")

        return chunks
