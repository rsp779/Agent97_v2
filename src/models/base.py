from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class AppModel(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True, populate_by_name=True)

