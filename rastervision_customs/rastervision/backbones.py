from enum import Enum

class CustomBackbone(Enum):
    # LTPA - LearnToPayAttention (POC-ing)
    LPTA_attention_before_pooling = "LPTA_attention_before_pooling"
    LPTA_attention_after_pooling = "LPTA_attention_after_pooling"

