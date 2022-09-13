from __future__ import annotations
from typing import Dict, Text, Any, List

from rasa.engine.graph import GraphComponent, ExecutionContext
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.nlu.tokenizers.tokenizer import Token

def _is_list_tokens(v):
    if isinstance(v, List):
        if len(v) > 0:
            if isinstance(v[0], Token):
                return True
    return False

# TODO: Correctly register your component with it's type
@DefaultV1Recipe.register(
    [DefaultV1Recipe.ComponentType.MESSAGE_TOKENIZER], is_trainable=False
)
class Printer(GraphComponent):
    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> Printer:
        # TODO: Implement this
        return cls()

    def train(self, training_data: TrainingData) -> Resource:
        # TODO: Implement this if your component requires training
        ...

    def process_training_data(self, training_data: TrainingData) -> TrainingData:
        # TODO: Implement this if your component augments the training data with
        #       tokens or message features which are used by other components
        #       during training.
        # components during training.
        ...
        print("printer-process_training_data")

        return training_data

    def process(self, messages: List[Message]) -> List[Message]:
        # TODO: This is the method which Rasa Open Source will call during inference.
        ...
        # if self.component_config['alias']:
        #     print("\n")
        #     print(self.component_config['alias'])
        for message in messages:
            # print(message.data)
            for k, v in message.data.items():
                # print(k, v)
                if _is_list_tokens(v):
                    print(f"{k}: {[t.text for t in v]}")
                else:
                    print(f"{k}: {v.__repr__()}")
            print("\n\n***********************MeSSAges**************************")
            print(message.data)
            print("\n\n\n\n")
        return messages
