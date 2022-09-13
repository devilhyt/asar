from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional, Text

from rasa.engine.graph import ExecutionContext, GraphComponent
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.constants import (
    ENTITY_ATTRIBUTE_CONFIDENCE,
    ENTITY_ATTRIBUTE_START,
    ENTITY_ATTRIBUTE_END,
    ENTITY_ATTRIBUTE_TYPE,
    ENTITY_ATTRIBUTE_VALUE,
    TEXT,
    ENTITIES,
)
from rasa.nlu.extractors.extractor import EntityExtractorMixin
from rasa.shared.nlu.training_data.message import Message

from ckip_transformers.nlp.util import NerToken

logger = logging.getLogger(__name__)


@DefaultV1Recipe.register(
    DefaultV1Recipe.ComponentType.ENTITY_EXTRACTOR,
    is_trainable=False,
)
class CkipTransformersExtractor(GraphComponent, EntityExtractorMixin):
    """Entity extractor which uses ckip-transformers (https://github.com/ckiplab/ckip-transformers)."""

    @staticmethod
    def supported_languages() -> Optional[List[Text]]:
        """Supported languages."""
        return ["zh"]

    @classmethod
    def required_packages(cls) -> List[Text]:
        """Lists required dependencies (see parent class for full docstring)."""
        return ["ckip_transformers"]

    @staticmethod
    def get_default_config() -> Dict[Text, Any]:
        """The component's default config (see parent class for full docstring)."""
        return {
            # by default all dimensions recognized by spacy are returned
            # dimensions can be configured to contain an array of strings
            # with the names of the dimensions to filter for
            "dimensions": None,

            # Parameters for creating driver.
            # (str optional, defaults to 3, must be 1—3) – The model level. The higher the level is, the more accurate and slower the model is.
            "level": 3,
            # (str optional, overwrites level) – The pretrained model name (e.g. 'ckiplab/bert-base-chinese-ner').
            "model_name": None,
            # (int, optional, defaults to -1,) – Device ordinal for CPU/GPU supports. Setting this to -1 will leverage CPU, a positive will run the model on the associated CUDA device id.
            "device": -1,

            # Parameters for calling the driver.
            # (bool, optional, defaults to False) – Segment sentence (internally) using delim_set.
            "use_delim": False,
            # (str, optional, defaults to '，,。：:；;！!？?') – Used for sentence segmentation if use_delim=True.
            "delim_set": "，,。：:；;！!？?",
            # (int, optional, defaults to 256) – The size of mini-batch.
            "batch_size": 256,
            # The maximum length of the sentence, must not longer then the maximum sequence length for this model (i.e. tokenizer.model_max_length).
            "max_length": None,
            # (int, optional, defaults to True) – Show progress bar
            "show_progress": True,
            # (bool, optional, defaults to True) – Pin memory in order to accelerate the speed of data transfer to the GPU. This option is incompatible with multiprocessing.
            "pin_memory": True,
        }

    def __init__(self, config: Dict[Text, Any]) -> None:
        """Initialize CkipTransformersExtractor."""
        self._config = config
        from ckip_transformers.nlp import CkipNerChunker
        self.ner_driver = CkipNerChunker(level=config["level"],
                                         model_name=config["model_name"],
                                         device=config["device"])

    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> CkipTransformersExtractor:
        """Creates a new component (see parent class for full docstring)."""
        return cls(config)

    def process(self, messages: List[Message]) -> List[Message]:
        """Extract entities using ckip-transformers.

        Args:
            messages: List of messages to process.

        Returns: The processed messages.
        """
        for message in messages:
            # can't use the existing doc here (spacy_doc on the message)
            # because tokens are lower cased which is bad for NER
            if message.get(TEXT):
                ner = self.ner_driver(input_text=[message.get(TEXT)],
                                      use_delim=self._config["use_delim"],
                                      delim_set=self._config["delim_set"],
                                      batch_size=self._config["batch_size"],
                                      max_length=self._config["max_length"],
                                      show_progress=self._config["show_progress"],
                                      pin_memory=self._config["pin_memory"])
                all_extracted = self.add_extractor_name(
                    self._extract_entities(ner[0]))
                dimensions = self._config["dimensions"]
                extracted = self.filter_irrelevant_entities(
                    all_extracted, dimensions)
                message.set(
                    ENTITIES, message.get(ENTITIES, []) + extracted, add_to_output=True
                )

        return messages

    @staticmethod
    def _extract_entities(ner: List[NerToken]) -> List[Dict[Text, Any]]:
        entities = [
            {
                ENTITY_ATTRIBUTE_TYPE: ner_sub.ner,
                ENTITY_ATTRIBUTE_VALUE: ner_sub.word,
                ENTITY_ATTRIBUTE_START: ner_sub.idx[0],
                ENTITY_ATTRIBUTE_CONFIDENCE: 1.0,
                ENTITY_ATTRIBUTE_END: ner_sub.idx[1],
            }
            for ner_sub in ner
        ]
        return entities
