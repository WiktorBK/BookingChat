import json
from pathlib import Path
from typing import Any, Text, Dict, List
from actions.main import RestaurantModel

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.knowledge_base.storage import InMemoryKnowledgeBase
from rasa_sdk.knowledge_base.actions import ActionQueryKnowledgeBase
from rasa_sdk.types import DomainDict
import re
import datetime

def isValidTime(time):
    try:
      if int(time) <= 24 and int(time) >= 0: return True
      return False
    except:
      regex = "^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
      p = re.compile(regex)
      if (time == ""): return False
      m = re.search(p, time)
      if m is None: return False
      return True

def ValidateDate(date):
  if date == "today": return True
  if date == "tomorrow": return True
  try:
      datetime.date.fromisoformat(date)
      return True
  except ValueError:
      return False


class ValidateBookingForm(FormValidationAction):
  def name(self) -> Text:
    return "validate_booking_form"

  def validate_hour(
    self, 
    slot_value: Any,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: DomainDict,
  ) -> Dict[Text, Any]:
    """ Validate 'hour' value """
    if isValidTime(slot_value) == False or isValidTime(slot_value) is None:
      dispatcher.utter_message(text="Wrong time format. Please use 24-hour format. ex: 17:00, 17")
      return {"hour": None}
    
    dispatcher.utter_message(text=f"All right, you want to book table at {slot_value}.")
    return {"hour": slot_value}

  def validate_guests(
    self, 
    slot_value: Any,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: DomainDict,
  ) -> Dict[Text, Any]:
    """ Validate 'guests' value """
    try:
      int(slot_value)
      dispatcher.utter_message(text=f"All right, you want to book table for {slot_value} guests.")
      return {"guests": slot_value}
    except:
      dispatcher.utter_message(text=f"Please enter the correct number of guests")
      return {"guests": None}

  def validate_date(
    self, 
    slot_value: Any,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: DomainDict,
  ) -> Dict[Text, Any]:
    """ Validate 'date' value """
    if ValidateDate(slot_value) == False or ValidateDate(slot_value) is None:
      dispatcher.utter_message(text="Wrong date format. Please use YYYY-MM-DD format")
      return {"date": None}
    
    dispatcher.utter_message(text=f"All right, you want to book table on {slot_value}.")
    return {"date": slot_value}




class ActionBookTable(Action):
    def name(self) -> Text:
      return "action_book_table"


class ActionCancelReservation(Action):
    def name(self) -> Text:
      return "action_cancel_reservation"


class ActionChangeReservation(Action):
    def name(self) -> Text:
      return "action_change_reservation"


class ActionCheckStatus(Action):
    def name(self) -> Text:
      return "action_check_status"


class ActionCheckAvailability(Action):
    def name(self) -> Text:
      return "action_check_availability"

