from rastervision.pipeline.config import register_config
from rastervision.pytorch_backend.pytorch_learner_backend_config import (
    PyTorchLearnerBackendConfig)
from rastervision.pytorch_learner.learner_config import default_augmentors
from rastervision.pytorch_learner.semantic_segmentation_learner_config import (
    SemanticSegmentationModelConfig, SemanticSegmentationLearnerConfig,
    SemanticSegmentationImageDataConfig)
from rastervision.pytorch_backend.pytorch_semantic_segmentation import (
    PyTorchSemanticSegmentation)


def ss_learner_backend_config_upgrader(cfg_dict, version):
    if version == 0:
        fields = {
            'augmentors': default_augmentors,
            'group_uris': None,
            'group_train_sz': None,
            'group_train_sz_rel': None,
            'num_workers': 4,
            'img_sz': None,
            'base_transform': None,
            'aug_transform': None,
            'plot_options': None,
            'preview_batch_limit': None
        }
        data_cfg_dict = {
            key: cfg_dict.pop(key, default_val)
            for key, default_val in fields.items() if key in cfg_dict
        }
        if data_cfg_dict.get('img_sz') is None:
            data_cfg_dict['img_sz'] = 256

        data_cfg = SemanticSegmentationImageDataConfig(**data_cfg_dict)
        data_cfg.update()
        data_cfg.validate_config()
        cfg_dict['data'] = data_cfg.dict()
    return cfg_dict


@register_config(
    'pytorch_semantic_segmentation_backend',
    upgrader=ss_learner_backend_config_upgrader)
class PyTorchSemanticSegmentationConfig(PyTorchLearnerBackendConfig):
    model: SemanticSegmentationModelConfig

    def get_learner_config(self, pipeline):
        learner = SemanticSegmentationLearnerConfig(
            data=self.data,
            model=self.model,
            solver=self.solver,
            test_mode=self.test_mode,
            output_uri=pipeline.train_uri,
            log_tensorboard=self.log_tensorboard,
            run_tensorboard=self.run_tensorboard)
        learner.update()
        learner.validate_config()
        return learner

    def build(self, pipeline, tmp_dir):
        learner = self.get_learner_config(pipeline)
        return PyTorchSemanticSegmentation(pipeline, learner, tmp_dir)
