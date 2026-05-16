import numpy as np
from collections import defaultdict


class TrackState:
    TENTATIVE = 1
    CONFIRMED = 2
    REMOVED = 3


class Track:
    def __init__(self, track_id, bbox, score):
        self.track_id = track_id
        self.bbox = bbox
        self.score = score
        self.state = TrackState.TENTATIVE
        self.hits = 1
        self.no_losses = 0
        self.age = 0
        self.centroid = self._compute_centroid(bbox)

    def _compute_centroid(self, bbox):
        x1, y1, x2, y2 = bbox
        return int((x1 + x2) / 2), int((y1 + y2) / 2)

    def update(self, bbox, score):
        self.bbox = bbox
        self.score = score
        self.centroid = self._compute_centroid(bbox)
        self.hits += 1
        self.no_losses = 0
        if self.state == TrackState.TENTATIVE and self.hits >= 3:
            self.state = TrackState.CONFIRMED

    def predict(self):
        self.age += 1
        self.no_losses += 1
        if self.no_losses > 30:
            self.state = TrackState.REMOVED

    @property
    def is_confirmed(self):
        return self.state == TrackState.CONFIRMED

    @property
    def is_removed(self):
        return self.state == TrackState.REMOVED


def iou(bbox1, bbox2):
    x1 = max(bbox1[0], bbox2[0])
    y1 = max(bbox1[1], bbox2[1])
    x2 = min(bbox1[2], bbox2[2])
    y2 = min(bbox1[3], bbox2[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    area1 = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
    area2 = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])
    union = area1 + area2 - inter
    return inter / union if union > 0 else 0


class ByteTracker:
    def __init__(self, track_high_thresh=0.5, track_low_thresh=0.1, match_thresh=0.8):
        self.track_id_counter = 0
        self.tracks = []
        self.track_high_thresh = track_high_thresh
        self.track_low_thresh = track_low_thresh
        self.match_thresh = match_thresh

    def update(self, detections):
        for t in self.tracks:
            t.predict()

        high_score = [d for d in detections if d["confidence"] >= self.track_high_thresh]
        low_score = [d for d in detections if self.track_low_thresh <= d["confidence"] < self.track_high_thresh]

        confirmed_tracks = [t for t in self.tracks if t.is_confirmed and not t.is_removed]

        matches_high, unmatched_dets_high, unmatched_tracks = self._match(confirmed_tracks, high_score)
        for track_idx, det_idx in matches_high:
            self.tracks[track_idx].update(
                high_score[det_idx]["bbox"],
                high_score[det_idx]["confidence"]
            )

        unmatched_confirmed = [self.tracks[i] for i in unmatched_tracks]
        matches_low, unmatched_dets_low, _ = self._match(unmatched_confirmed, low_score)
        for track_idx, det_idx in matches_low:
            self.tracks[track_idx].update(
                low_score[det_idx]["bbox"],
                low_score[det_idx]["confidence"]
            )

        for det_idx in unmatched_dets_high:
            self.track_id_counter += 1
            new_track = Track(
                self.track_id_counter,
                high_score[det_idx]["bbox"],
                high_score[det_idx]["confidence"]
            )
            new_track.state = TrackState.CONFIRMED
            self.tracks.append(new_track)

        unconfirmed_tracks = [t for t in self.tracks if t.state == TrackState.TENTATIVE and not t.is_removed]
        matches_rem, unmatched_dets_rem, _ = self._match(unconfirmed_tracks, high_score)
        for track_idx, det_idx in matches_rem:
            self.tracks[track_idx].update(
                high_score[det_idx]["bbox"],
                high_score[det_idx]["confidence"]
            )

        self.tracks = [t for t in self.tracks if not t.is_removed]
        return self._get_active_tracks()

    def _match(self, tracks, detections):
        if not tracks or not detections:
            return [], list(range(len(detections))), list(range(len(tracks)))

        cost_matrix = np.zeros((len(tracks), len(detections)))
        for i, t in enumerate(tracks):
            for j, d in enumerate(detections):
                cost_matrix[i, j] = iou(t.bbox, d["bbox"])

        matches = []
        unmatched_tracks = list(range(len(tracks)))
        unmatched_dets = list(range(len(detections)))

        for _ in range(min(len(tracks), len(detections))):
            if cost_matrix.size == 0:
                break
            idx = np.argmax(cost_matrix)
            i, j = np.unravel_index(idx, cost_matrix.shape)
            if cost_matrix[i, j] < self.match_thresh:
                break
            matches.append((unmatched_tracks[i], unmatched_dets[j]))
            cost_matrix = np.delete(cost_matrix, i, axis=0)
            cost_matrix = np.delete(cost_matrix, j, axis=1)
            unmatched_tracks.pop(i)
            unmatched_dets.pop(j)

        return matches, unmatched_dets, unmatched_tracks

    def _get_active_tracks(self):
        results = []
        for t in self.tracks:
            if t.is_confirmed:
                results.append({
                    "track_id": t.track_id,
                    "bbox": t.bbox,
                    "score": t.score,
                    "centroid": t.centroid
                })
        return results
