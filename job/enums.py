from enum import Enum

class PaymentTypeEnum(Enum):
    FIXED = "Fixed Price"
    HOURLY = "Hourly Rate"
    MILESTONE = "Milestone Based"
    PROJECT = "Project Based"

    @classmethod
    def choices(cls):
        return [(item.name, item.value) for item in cls]

class TimePreferenceEnum(Enum):
    FULL_TIME = "Full Time"
    PART_TIME = "Part Time"
    FLEXIBLE = "Flexible Hours"
    CONTRACT = "Contract Based"
    CUSTOM = "CUSTOM"

    @classmethod
    def choices(cls):
        return [(item.name, item.value) for item in cls]

class ExperienceLevelEnum(Enum):
    ENTRY = "Entry Level"
    INTERMEDIATE = "Intermediate"
    EXPERT = "Expert"
    ALL = "All Levels"

    @classmethod
    def choices(cls):
        return [(item.name, item.value) for item in cls]

class LocationEnum(Enum):
    REMOTE = "Remote"
    ONSITE = "On-site"
    HYBRID = "Hybrid"

    @classmethod
    def choices(cls):
        return [(item.name, item.value) for item in cls]

class StatusEnum(Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CLOSED = "Closed"

    @classmethod
    def choices(cls):
        return [(item.name, item.value) for item in cls]

class ProposalStatusEnum(Enum):
    PENDING = 'PENDING'
    ACCEPTED = 'ACCEPTED'
    REJECTED = 'REJECTED'
    
    @classmethod
    def choices(cls):
        return [
            (item.value, item.value.title()) 
            for item in cls
        ]