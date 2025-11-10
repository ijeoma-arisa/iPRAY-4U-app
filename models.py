class PrayerRequest:
  def __init__(self):
    pass

class Person:  
  def __init__(self, id: str, name: str, relationship: str):
    # TO DO: Generate id
    self.id = id
    self.name = name
    self.relationship = relationship
    self.prayer_requests = []
    
  def __repr__(self):
    # TO DO: Fix the prayer_requests output
    return f"Person(id={self.id}, name={self.name}, relationship={self.relationship}, prayer_requests={self.prayer_requests})"
  
  def __str__(self):
    return f"""{self.name} ({self.relationship})
  Prayer Requests: {self.prayer_requests}"""
  
  def __eq__(self, person):
    if person is Person and self.id == person.id:
      return True
    return False
    
  def set_id(self, id: str):
    self.id = id
    
  def get_id(self) -> str:
    return self.id
  
  def set_name(self, name: str) -> None:
    self.name = name
    
  def get_name(self) -> str:
    return self.name
  
  def set_relationship(self, relationship) -> None:
    self.relationship = relationship
    
  def get_relationship(self) -> str:
    return self.relationship
  
  def add_prayer_request(self, prayer_request: PrayerRequest) -> None:
    self.prayer_requests.append(prayer_request)
    
  def delete_prayer_request(self, prayer_request_id: str) -> bool:
      for i, prayer_request in self.prayer_requests:
        if prayer_request.id == prayer_request_id:
          self.prayer_requests.pop(i)
          return True
      return False
      
    
  

  
    