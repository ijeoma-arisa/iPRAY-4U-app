from typing import Optional
from enum import Enum

class Relationship(Enum):
  # TO DO: Add a way to designate it as favorite
  FAMILY = "Family"
  FRIENDS = "Friends"
  MINISTRY = "Ministry"
  # TO DO: Implement custom feature
  CUSTOM = "Custom"


class Prayer:
  def __init__(self, text: Optional[str] = None, has_prayed: bool = False):
    self._id = None
    self._text = text
    self._has_prayed = has_prayed
    
  def get_id(self): 
    return self._id
  
  def set_id(self, id):
    self._id = id
    
  def get_text(self):
    return self._text
  
  def set_text(self, text: str):
    self._text = text
  
  def set_has_prayed(self, prayed: bool) -> None:
    self._has_prayed = prayed
      
  def has_prayed(self) -> bool:
    return self._has_prayed
  
  def to_dict(self) -> dict:
    return {"id": self._id, "text": self._text, "has_prayed": self._has_prayed}


class Person:  
  def __init__(self, id: str, name: str, relationship: Relationship):
    # TO DO: Generate id
    self._id = id
    self._name = name
    self._relationship = relationship
    self._prayer_requests = []
    
  def __repr__(self):
    # TO DO: Fix the prayer_requests output
    return f"Person(id={self._id}, name={self._name}, relationship={self._relationship}, prayer_requests={self._prayer_requests})"
  
  def __str__(self):
    return f"""{self._name} ({self._relationship.value})
  Prayer Requests: {self._prayer_requests}"""
  
  def __eq__(self, person):
    if person is Person and self._id == person.id:
      return True
    return False
    
  def set_id(self, id: str):
    self._id = id
    
  def get_id(self) -> str:
    return self._id
  
  def set_name(self, name: str) -> None:
    self._name = name
    
  def get_name(self) -> str:
    return self._name
  
  def set_relationship(self, relationship: Relationship) -> None:
    self._relationship = relationship
    
  def get_relationship(self) -> Relationship:
    return self._relationship
  
  def get_prayer_requests(self) -> list[Prayer]:
    return self._prayer_requests
    
  def add_prayer_request(self, prayer_request: Prayer) -> None:
    prayer_id = self._prayer_requests[-1].get_id() + 1 if self._prayer_requests else 1
    prayer_request.set_id(prayer_id)
    self._prayer_requests.append(prayer_request)
    
  def delete_prayer_request(self, prayer_request_id: str) -> bool:
      for i, prayer_request in self._prayer_requests:
        if prayer_request.get_id() == prayer_request_id:
          self._prayer_requests.pop(i)
          return True
      return False
    
  def to_dict(self) -> dict:
    return {
        "id": self._id,
        "name": self._name,
        "relationship": self._relationship.value,
        "prayer_requests": [prayer.to_dict() for prayer in self._prayer_requests]
      }

    