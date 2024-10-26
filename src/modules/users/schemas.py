__all__ = ["ViewUser"]

from datetime import datetime

from src.pydantic_base import BaseSchema

class Profile(BaseSchema):
    id: str
    "User id on sports website"
    name: str
    "User's first and last name"
    email: str
    "User university email"
    medical_group: str
    "User medical group for sport"

class Checkin(BaseSchema):
    title: str
    "Sport name"
    start: str
    "Training start time"
    end: str
    "End time of training"
    training_class: str
    "Place of training"
    group_accredited: bool
    "Accreditation of training"


class Semester(BaseSchema):
    id_sem: int
    "Semester id"
    hours_not_self: int
    "Earned hours of training by appointment"
    hours_self_not_debt: int
    "Hours earned in personal training"
    hours_self_debt: int
    "Earned hours in personal training to cover hours debt"
    hours_sem_max: int
    "Number of hours required to complete the semester"
    debt: int
    "User's hours debt for previous semesters"


class Training(BaseSchema):
    hours: int
    "Duration of training"
    group: str
    "Sport name"
    timestamp: datetime
    "Training start time"
    approved: bool
    "Hours approval"


class ViewUser(BaseSchema):
    profile: Profile
    ""
    checkins: list[Checkin]
    "List of workouts the user has signed up for in the coming week"
    old_semesters: list[Semester]
    "Hours earned for past semesters"
    ongoing_semester: Semester
    "Current semester"
    trainings_history: list[Training]
    "List of attended trainings for the current semester"
