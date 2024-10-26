from datetime import datetime, timedelta, tzinfo, timezone

import httpx
from fastapi import APIRouter

from src.api.dependencies import CURRENT_USER_ID_DEPENDENCY
from src.api.exceptions import IncorrectCredentialsException
from src.logging_ import logger
from src.modules.innohassle_accounts import innohassle_accounts
from src.modules.users.schemas import ViewUser

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={
        **IncorrectCredentialsException.responses,
    },
)

INNOSPORT_URL = "https://sport.innopolis.university/api/"


def get_authorized_client(sport_token) -> httpx.AsyncClient:
    return httpx.AsyncClient(headers={"Authorization": f"Bearer {sport_token}"}, base_url=INNOSPORT_URL)


@router.get("/sport_info", responses={200: {"description": "Current sport info for user"}})
async def get_me(innohassle_id: CURRENT_USER_ID_DEPENDENCY) -> ViewUser:
    """
    Get current sport hours, semesters info, and nearest check-ins
    """
    sport_token = await innohassle_accounts.get_sport_token(innohassle_id)
    logger.info(sport_token)

    async with get_authorized_client(sport_token) as client:
        response = await client.get("profile/student")
        response.raise_for_status()
        profile = response.json()
        user_id = profile["id"]

        response = await client.get(f"attendance/{user_id}/hours")
        response.raise_for_status()
        semesters = response.json()
        old_trainings = semesters["last_semesters_hours"]
        ongoing_semester = response.json()["ongoing_semester"]

        params = {"start": datetime.now().isoformat(), "end": (datetime.now() + timedelta(weeks=1)).isoformat()}
        response = await client.get("calendar/trainings", params=params)
        response.raise_for_status()
        checkins = [training for training in response.json() if training["extendedProps"]["checked_in"]]
        checkins = [
            {
                "title": training["title"],
                "start": training["start"],
                "end": training["end"],
                "training_class": training["extendedProps"]["training_class"],
                "group_accredited": training["extendedProps"]["group_accredited"],
            }
            for training in checkins
        ]

        response = await client.get(f"profile/history_with_self/{ongoing_semester["id_sem"]}", params=params)
        response.raise_for_status()
        trainings_history = response.json()["trainings"]
        trainings_history = [
            {
                "hours": training["hours"],
                "group": training["group"],
                "timestamp": datetime.strptime(training["timestamp"], "%b %d %H:%M").replace(
                    year=datetime.now().year, tzinfo=timezone(timedelta(hours=3))
                ),
                "approved": training["approved"],
            }
            for training in trainings_history
        ]

        data = {
            "profile": profile,
            "checkins": checkins,
            "old_semesters": old_trainings,
            "ongoing_semester": ongoing_semester,
            "trainings_history": trainings_history,
        }
        return ViewUser.model_validate(data)
