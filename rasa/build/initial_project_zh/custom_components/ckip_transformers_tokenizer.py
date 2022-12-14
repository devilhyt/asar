from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional, Text

from rasa.engine.graph import ExecutionContext
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.nlu.tokenizers.tokenizer import Token, Tokenizer
from rasa.shared.nlu.training_data.message import Message

logger = logging.getLogger(__name__)


@DefaultV1Recipe.register(
    DefaultV1Recipe.ComponentType.MESSAGE_TOKENIZER,
    is_trainable=False
)
class CkipTransformersTokenizer(Tokenizer):
    """Tokenizer that uses ckip-transformers (https://github.com/ckiplab/ckip-transformers)."""

    @staticmethod
    def supported_languages() -> Optional[List[Text]]:
        """Supported languages."""
        return ["zh"]

    @staticmethod
    def required_packages() -> List[Text]:
        """Any extra python dependencies required for this component to run."""
        return ["ckip_transformers"]

    @staticmethod
    def get_default_config() -> Dict[Text, Any]:
        """Returns default config."""
        return {
            # Rasa
            # Flag to check whether to split intents
            "intent_tokenization_flag": False,
            # Symbol on which intent should be split
            "intent_split_symbol": "_",
            # Regular expression to detect tokens
            "token_pattern": None,

            # Parameters for creating driver.
            # model (str optional, defaults to “bert-base”.) – The pretrained model name provided by CKIP Transformers.
            "model": 'albert-base',
            # model_name (str optional, overwrites model) – The custom pretrained model name (e.g. 'ckiplab/bert-base-chinese-ws').
            "model_name": None,
            # device (int or torch.device, optional, defaults to -1) – Device ordinal for CPU/GPU supports. Setting this to -1 will leverage CPU, a positive will run the model on the associated CUDA device id.
            "device": -1,

            # Parameters for calling the driver.
            # use_delim (bool, optional, defaults to False) – Segment sentence (internally) using delim_set.
            "use_delim": True,
            # delim_set (str, optional, defaults to '，,。：:；;！!？?') – Used for sentence segmentation if use_delim=True.
            "delim_set": "，,。：:；;！!？? ",
            # batch_size (int, optional, defaults to 256) – The size of mini-batch.
            "batch_size": 256,
            # max_length (int, optional) – The maximum length of the sentence, must not longer then the maximum sequence length for this model (i.e. tokenizer.model_max_length).
            "max_length": None,
            # show_progress (int, optional, defaults to True) – Show progress bar.
            "show_progress": True,
            # pin_memory (bool, optional, defaults to True) – Pin memory in order to accelerate the speed of data transfer to the GPU. This option is incompatible with multiprocessing.
            "pin_memory": True,
        }

    def __init__(self, config: Dict[Text, Any]) -> None:
        super().__init__(config)
        from ckip_transformers.nlp import CkipWordSegmenter
        self.ws_driver = CkipWordSegmenter(model=config["model"],
                                           model_name=config["model_name"],
                                           device=config["device"])

    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> CkipTransformersTokenizer:
        """Creates a new component (see parent class for full docstring)."""
        return cls(config)

    def tokenize(self, message: Message, attribute: Text) -> List[Token]:
        """Tokenizes the text of the provided attribute of the incoming message."""

        text = message.get(attribute)

        if not text:
            ws = [[text]]
        else:
            ws = self.ws_driver(input_text=[text],
                                use_delim=self._config["use_delim"],
                                delim_set=self._config["delim_set"],
                                batch_size=self._config["batch_size"],
                                max_length=self._config["max_length"],
                                show_progress=self._config["show_progress"],
                                pin_memory=self._config["pin_memory"]
                                )
        # Delete whitespace
        tokenized = [w for w in ws[0] if w and w.strip()]

        # Convert words to tokens
        tokens = self._convert_words_to_tokens(tokenized, text)

        return self._apply_token_pattern(tokens)
