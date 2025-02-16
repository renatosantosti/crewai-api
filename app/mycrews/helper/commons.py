from enum import Enum

class DateEntityEnum(Enum):
    DATE = "DATE"
    DATE_TIME = "DATE_TIME"
    
class NumericEntityEnum(Enum):
    MONEY = "MONEY"
    MEASURE = "MEASURE"
    NUMBER = "NUMBER"
    
class WebEntityEnum(Enum):
    EMAIL = "EMAIL"
    URL = "URL"
    
  
class TextEntityEnum(Enum):
    PERSON = "PERSON"
    ORG = "ORG"
    LOCATION = "LOCATION"
    