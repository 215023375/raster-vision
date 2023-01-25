from typing import (TYPE_CHECKING, Any, Dict, Iterable, List, Optional,
                    Sequence, Tuple)
from dataclasses import dataclass

import numpy as np

from rastervision.core.box import Box
from rastervision.core.data.label import Labels

if TYPE_CHECKING:
    from rastervision.core.data import (ClassConfig, CRSTransformer)
    from shapely.geometry import Polygon


@dataclass
class ClassificationLabel:
    class_id: int
    scores: Optional[Sequence[float]] = None

    def __iter__(self):
        return iter((self.class_id, self.scores))


class FullWindowClassificationLabels(Labels):
    """Represents whole scene image (no grid) associated with classes."""

    def __init__(self,
                 scene_to_label: Optional[Dict[Scene.id, Tuple[int, Optional[
                     Sequence[float]]]]] = None):
        if scene_to_label is None:
            scene_to_label = {}

        self.scene_to_label = {
            scene: ClassificationLabel(*label)
            for scene, label in scene_to_label.items()
        }

    def __len__(self) -> int:
        return len(self.scene_to_label)

    def __eq__(self, other: 'FullWindowClassificationLabels') -> bool:
        return (isinstance(other, FullWindowClassificationLabels)
                and self.scene_to_label == other.scene_to_label)

    def __add__(self, other: 'FullWindowClassificationLabels'
                ) -> 'FullWindowClassificationLabels':
        result = FullWindowClassificationLabels()
        result.extend(self)
        result.extend(other)
        return result

    def __contains__(self, cell: Box) -> bool:
        return cell in self.scene_to_label

    def __getitem__(self, scene: Scene) -> ClassificationLabel:
        return self.scene_to_label[scene.id]

    def __setitem__(self, scene: Scene,
                    value: Tuple[int, Optional[Sequence[float]]]):
        class_id, scores = value
        self.set_cell(scene.id, class_id, scores=scores)

    @classmethod
    def from_predictions(cls, scenes: Iterable[Scene],
                         predictions: Iterable[Any]) -> 'Labels':
        """Overrid to convert predictions to (class_id, scores) pairs."""
        predictions = ((np.argmax(p), p) for p in predictions)
        return super().from_predictions(scenes, predictions)

    @classmethod
    def make_empty(cls) -> 'FullWindowClassificationLabels':
        return FullWindowClassificationLabels()

    def set_cell(self,
                 scene_id: Scene.id,
                 class_id: int,
                 scores: Optional['np.ndarray'] = None) -> None:
        """Set cell and its class_id.

        Args:
            scene_id: (Scene.id)
            class_id: int
            scores: 1d numpy array of probabilities for each class
        """
        if scores is not None:
            scores = list(map(lambda x: float(x), list(scores)))
        class_id = int(class_id)
        self.scene_to_label[scene_id] = ClassificationLabel(class_id, scores)

    def get_cell_class_id(self, cell: Box) -> int:
        """Return class_id for a cell.

        Args:
            cell: (Box)
        """
        result = self.scene_to_label.get(cell)
        if result is not None:
            return result.class_id
        else:
            return None

    def get_cell_scores(self, cell: Box) -> Optional[Sequence[float]]:
        """Return scores for a cell.

        Args:
            cell: (Box)
        """
        result = self.scene_to_label.get(cell)
        if result is not None:
            return result.score
        else:
            return None

    def get_singleton_labels(self, cell: Box):
        """Return Labels object representing a single cell.

        Args:
            cell: (Box)
        """
        return FullWindowClassificationLabels({cell: self[cell]})

    def get_cells(self) -> List[Box]:
        """Return list of all cells (list of Box)."""
        return list(self.scene_to_label.keys())

    def get_class_ids(self) -> List[int]:
        """Return list of class_ids for all cells."""
        return [label.class_id for label in self.scene_to_label.values()]

    def get_scores(self) -> List[Optional[Sequence[float]]]:
        """Return list of scores for all cells."""
        return [label.scores for label in self.scene_to_label.values()]

    def get_values(self) -> List[ClassificationLabel]:
        """Return list of class_ids and scores for all cells."""
        return list(self.scene_to_label.values())

    def extend(self, labels: 'FullWindowClassificationLabels') -> None:
        """Adds cells contained in labels.

        Args:
            labels: FullWindowClassificationLabels
        """
        for cell in labels.get_cells():
            self.set_cell(cell, )

    def save(self, uri: str, class_config: 'ClassConfig',
             crs_transformer: 'CRSTransformer') -> None:
        """Save labels as a GeoJSON file.

        Args:
            uri (str): URI of the output file.
            class_config (ClassConfig): ClassConfig to map class IDs to names.
            crs_transformer (CRSTransformer): CRSTransformer to convert from
                pixel-coords to map-coords before saving.
        """
        from rastervision.core.data import ChipClassificationGeoJSONStore

        label_store = ChipClassificationGeoJSONStore(
            uri=uri,
            class_config=class_config,
            crs_transformer=crs_transformer)
        label_store.save(self)