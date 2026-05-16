class LineCounter:
    def __init__(self, line_y=None, direction="down"):
        self.count = 0
        self.counted_ids = set()
        self.line_y = line_y
        self.direction = direction
        self.prev_positions = {}

    def set_line(self, line_y):
        self.line_y = line_y

    def update(self, track_id, centroid):
        if track_id in self.counted_ids:
            return False

        if self.line_y is None:
            return False

        cy = centroid[1]

        if track_id in self.prev_positions:
            prev_cy = self.prev_positions[track_id]
            if self.direction == "down":
                if prev_cy < self.line_y <= cy:
                    self.count += 1
                    self.counted_ids.add(track_id)
                    return True
            elif self.direction == "up":
                if prev_cy > self.line_y >= cy:
                    self.count += 1
                    self.counted_ids.add(track_id)
                    return True
            else:
                if (prev_cy < self.line_y <= cy) or (prev_cy > self.line_y >= cy):
                    self.count += 1
                    self.counted_ids.add(track_id)
                    return True

        self.prev_positions[track_id] = cy
        return False

    def reset(self):
        self.count = 0
        self.counted_ids.clear()
        self.prev_positions.clear()


class MultiLineCounter:
    def __init__(self):
        self.counters = {}

    def add_line(self, name, line_y, direction="down"):
        self.counters[name] = LineCounter(line_y, direction)

    def update(self, track_id, centroid):
        results = {}
        for name, counter in self.counters.items():
            results[name] = counter.update(track_id, centroid)
        return results

    def get_counts(self):
        return {name: c.count for name, c in self.counters.items()}

    def reset(self):
        for c in self.counters.values():
            c.reset()
