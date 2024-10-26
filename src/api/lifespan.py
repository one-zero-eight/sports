__all__ = ["lifespan"]

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.modules.innohassle_accounts import innohassle_accounts


@asynccontextmanager
async def lifespan(app: FastAPI):
    # await setup_repositories()
    await innohassle_accounts.update_key_set()
    yield
