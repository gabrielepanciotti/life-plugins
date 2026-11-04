from __future__ import annotations

import re

from pydantic import BaseModel, Field, computed_field, field_validator

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class EntityType(BaseModel):
    """A canonical domain page type (generates a file in vault/_templates/)."""

    name: str
    fields: list[str] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def _slug(cls, v: str) -> str:
        if not SLUG_RE.match(v):
            raise ValueError(f"entity name must be kebab-case: {v!r}")
        return v


class ScaffoldConfig(BaseModel):
    """All settings needed to generate a digital knowledge vault (mini-interview answers)."""

    project_name: str
    persona: str
    persona_full: str | None = None
    mission: str
    aliases: list[str] = Field(min_length=1)
    scope: str
    host_root: str | None = None
    wiki_domains: list[str] = Field(min_length=1)
    entity_types: list[EntityType] = Field(default_factory=list)
    decision_queries: list[str] = Field(default_factory=list)
    tier: int = 0

    @field_validator("project_name")
    @classmethod
    def _name_slug(cls, v: str) -> str:
        if not SLUG_RE.match(v):
            raise ValueError(f"project_name must be kebab-case: {v!r}")
        return v

    @field_validator("scope")
    @classmethod
    def _scope(cls, v: str) -> str:
        if v not in {"personal", "work"}:
            raise ValueError(f"scope must be 'personal' or 'work', got {v!r}")
        return v

    @field_validator("tier")
    @classmethod
    def _tier(cls, v: int) -> int:
        if v not in (0, 1):
            raise ValueError(f"tier must be 0 or 1, got {v!r}")
        return v

    @field_validator("host_root")
    @classmethod
    def _strip_host_root_sep(cls, v: str | None) -> str | None:
        return v.rstrip("\\") if v else v

    @computed_field
    @property
    def host_base(self) -> str:
        if self.host_root:
            return self.host_root
        return "G:" if self.scope == "personal" else "Z:"

    @computed_field
    @property
    def project_dir(self) -> str:
        # Windows path — this tool is Windows-only.
        return f"{self.host_base}\\{self.project_name}"

    @computed_field
    @property
    def db_name(self) -> str:
        return self.project_name.replace("-", "_")
