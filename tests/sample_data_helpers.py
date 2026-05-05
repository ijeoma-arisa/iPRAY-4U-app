def generate_sample_person(name=None, relationship=None, prayer=None):
      data = {}
      
      if name is not None:
          data["name"] = name
      
      if relationship is not None:
          data["relationship"] = relationship
          
      if prayer is not None:
          data["prayer"] = prayer
          
      return data    