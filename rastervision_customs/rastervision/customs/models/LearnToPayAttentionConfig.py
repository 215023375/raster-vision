from rastervision.pytorch_learner import ClassificationModelConfig
from typing import (Optional)
from rastervision.pipeline.config import (register_config, Field)
from torch import nn
from rastervision.customs import CustomBackbone

from rastervision.customs.models.LearnToPayAttention.model1 import AttnVGG_before


# Annotation not working as expected,  needs to be built into rastervision. Adding manually at the end of file
@register_config(CustomBackbone.LPTA_attention_after_pooling.value)
class LTPAAfterPoolingVGGModelConfig(ClassificationModelConfig):
    """Config related to models."""
    backbone: CustomBackbone = Field(
        CustomBackbone.LPTA_attention_after_pooling,
        description=(
            "default backbone"
        ))
    pretrained: bool = Field(
        False,
        description=(
            'If True, use ImageNet weights. If False, use random initialization.'
        ))
    init_weights: Optional[str] = Field(
        None,
        description=('URI of PyTorch model weights used to initialize model. '
                     'If set, this supercedes the pretrained option.'))

    def get_backbone_str(self):
        return self.backbone.name

    def build(self,
              num_classes: int,
              in_channels: int,
              save_dir: Optional[str] = None,
              hubconf_dir: Optional[str] = None,
              **kwargs) -> nn.Module:
        """Build and return a model based on the config.

        Args:
            num_classes (int): Number of classes.
            in_channels (int, optional): Number of channels in the images that
                will be fed into the model. Defaults to 3.
            save_dir (Optional[str], optional): Used for building external_def
                if specified. Defaults to None.
            hubconf_dir (Optional[str], optional): Used for building
                external_def if specified. Defaults to None.

        Returns:
            nn.Module: a PyTorch nn.Module.
        """
        if self.external_def is not None:
            return self.build_external_model(
                save_dir=save_dir, hubconf_dir=hubconf_dir)
        return self.build_default_model(num_classes, in_channels, **kwargs)

    def build_default_model(self, num_classes: int, in_channels: int,
                            **kwargs) -> nn.Module:
        """Build and return the default model.

        Args:
            num_classes (int): Number of classes.
            in_channels (int, optional): Number of channels in the images that
                will be fed into the model. Defaults to 3.

        Returns:
            nn.Module: a PyTorch nn.Module.
        """
        # TODO: Use more of the fields available
        print(f"[Building model] backbone string: {self.get_backbone_str()}")
        return AttnVGG_before(512, num_classes)