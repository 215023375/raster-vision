from typing import Any, Callable
import unittest
from os.path import join
from uuid import uuid4
import logging

import numpy as np
import torch

from rastervision.pipeline import rv_config
from rastervision.pipeline.file_system import json_to_file
from rastervision.core.data import (
    ClassConfig, DatasetConfig, RasterioSourceConfig, MultiRasterSourceConfig,
    ReclassTransformerConfig, SceneConfig, ChipClassificationLabelSourceConfig,
    GeoJSONVectorSourceConfig, ClassInferenceTransformerConfig)
from rastervision.core.rv_pipeline import ChipClassificationConfig
from rastervision.pytorch_backend import PyTorchChipClassificationConfig
from rastervision.pytorch_learner import (
    ClassificationModelConfig, SolverConfig, ClassificationGeoDataConfig,
    PlotOptions, GeoDataWindowConfig)
from tests import data_file_path


def make_scene(num_channels: int, num_classes: int,
               tmp_dir: str) -> SceneConfig:
    path = data_file_path('multi_raster_source/const_100_600x600.tiff')
    rs_cfgs_img = []
    for _ in range(num_channels):
        rs_cfg = RasterioSourceConfig(
            uris=[path],
            channel_order=[0],
            transformers=[
                ReclassTransformerConfig(
                    mapping={100: np.random.randint(0, 256)})
            ])
        rs_cfgs_img.append(rs_cfg)
    rs_cfg_img = MultiRasterSourceConfig(
        raster_sources=rs_cfgs_img, channel_order=list(range(num_channels)))

    geojson = {
        'type':
        'FeatureCollection',
        'features': [{
            'properties': {
                'class_id': np.random.randint(0, num_classes)
            },
            'geometry': {
                'type': 'Point',
                'coordinates': [np.random.sample(),
                                np.random.sample()]
            }
        } for _ in range(2)]
    }
    uri = join(tmp_dir, 'labels.json')
    json_to_file(geojson, uri)
    label_source_cfg = ChipClassificationLabelSourceConfig(
        vector_source=GeoJSONVectorSourceConfig(
            uri=uri,
            transformers=[ClassInferenceTransformerConfig(default_class_id=0)
                          ]),
        background_class_id=0)
    scene_cfg = SceneConfig(
        id=str(uuid4()),
        raster_source=rs_cfg_img,
        label_source=label_source_cfg)
    return scene_cfg


class TestClassificationLearner(unittest.TestCase):
    def assertNoError(self, fn: Callable, msg: str = ''):
        try:
            fn()
        except Exception:
            self.fail(msg)

    def test_learner(self):
        self.assertNoError(lambda: self._test_learner(3, None))
        self.assertNoError(
            lambda: self._test_learner(6, [(0, 1, 2), (3, 4, 5)]))

    def _test_learner(self,
                      num_channels: int,
                      channel_display_groups: Any,
                      num_classes: int = 5):
        """Tests whether the learner can be instantiated correctly and
        produce plots."""
        logging.disable(logging.CRITICAL)

        with rv_config.get_tmp_dir() as tmp_dir:
            class_config = ClassConfig(
                names=[f'class_{i}' for i in range(num_classes)])
            dataset_cfg = DatasetConfig(
                class_config=class_config,
                train_scenes=[
                    make_scene(num_channels, num_classes, tmp_dir)
                    for _ in range(2)
                ],
                validation_scenes=[
                    make_scene(num_channels, num_classes, tmp_dir)
                    for _ in range(2)
                ],
                test_scenes=[])
            data_cfg = ClassificationGeoDataConfig(
                scene_dataset=dataset_cfg,
                window_opts=GeoDataWindowConfig(size=20, stride=20),
                class_names=class_config.names,
                class_colors=class_config.colors,
                plot_options=PlotOptions(
                    channel_display_groups=channel_display_groups),
                num_workers=0)
            backend_cfg = PyTorchChipClassificationConfig(
                data=data_cfg,
                model=ClassificationModelConfig(pretrained=False),
                solver=SolverConfig(),
                log_tensorboard=False)
            pipeline_cfg = ChipClassificationConfig(
                root_uri=tmp_dir, dataset=dataset_cfg, backend=backend_cfg)
            pipeline_cfg.update()
            backend = backend_cfg.build(pipeline_cfg, tmp_dir)
            learner = backend.learner_cfg.build(tmp_dir, training=True)
            learner.plot_dataloaders()
            learner.plot_predictions(split='valid')

            torch.save(learner.model.state_dict(),
                       learner.last_model_weights_path)
            learner.save_model_bundle()

            pred_scene = dataset_cfg.validation_scenes[0].build(
                class_config, tmp_dir)
            _ = backend.predict_scene(pred_scene, chip_sz=100)


if __name__ == '__main__':
    unittest.main()
