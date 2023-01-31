import json
from pathlib import Path
from typing import Any, Text, Dict, List
from actions.main import Binance

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.knowledge_base.storage import InMemoryKnowledgeBase
from rasa_sdk.knowledge_base.actions import ActionQueryKnowledgeBase



class ActionGetPrice(Action):

    def name(self) -> Text:
      return "action_get_price"

    def run(self,
           dispatcher: CollectingDispatcher,
           tracker: Tracker,
           domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        for entity in tracker.latest_message['entities']:
            print(tracker.latest_message)
            if entity['entity'] == 'symbol':
                symbol = entity['value']
                

                
            else:
                    dispatcher.utter_message(
                        text=f"I do not recognize {symbol}, are you sure it is correctly spelled?")
        return []
