from dataclasses import dataclass


@dataclass
class Nfa:
    edges: list[list[tuple[str | None, int]]]
    start: int
    accept: int

    def state(self) -> int:
        self.edges.append([])
        return len(self.edges) - 1

    def edge(self, source: int, char: str | None, target: int) -> None:
        self.edges[source].append((char, target))

    def closure(self, states: set[int]) -> frozenset[int]:
        reached = set(states)
        pending = list(states)
        while pending:
            source = pending.pop()
            for char, target in self.edges[source]:
                if char is None and target not in reached:
                    reached.add(target)
                    pending.append(target)
        return frozenset(reached)

    def first(self) -> frozenset[int]:
        return self.closure({self.start})

    def step(self, states: frozenset[int], char: str) -> frozenset[int]:
        targets = {
            target
            for source in states
            for edge_char, target in self.edges[source]
            if edge_char == char
        }
        return self.closure(targets)

    def accepts(self, states: frozenset[int]) -> bool:
        return self.accept in states
