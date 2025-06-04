from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, ConfigDict, HttpUrl


# Helper model for common PokeAPI name-url pairs
class NameUrlDetail(BaseModel):
    name: str
    url: HttpUrl


class PokemonType(BaseModel):
    """Pokemon type schema, reflecting PokeAPI structure"""
    slot: int
    type: NameUrlDetail


class PokemonAbility(BaseModel):
    """Pokemon ability schema, reflecting PokeAPI structure"""
    slot: int
    is_hidden: bool
    ability: NameUrlDetail


class PokemonStat(BaseModel):
    """Pokemon stat schema, reflecting PokeAPI structure"""
    base_stat: int
    effort: int
    stat: NameUrlDetail


class PokemonBase(BaseModel):
    """Base Pokemon schema for data we store/process"""
    pokemon_id: int = Field(..., description="Pokemon ID from PokeAPI")
    name: str = Field(..., description="Pokemon name")
    height: float = Field(..., description="Pokemon height")
    weight: float = Field(..., description="Pokemon weight")
    base_experience: int = Field(..., description="Base experience")
    types: List[str] = Field(..., description="Pokemon types (list of names)")
    abilities: List[str] = Field(..., description="Pokemon abilities (list of names)")
    stats: Dict[str, int] = Field(..., description="Pokemon stats (name: base_stat)")
    sprite_front: Optional[HttpUrl] = Field(default=None, description="Front sprite URL")
    sprite_back: Optional[HttpUrl] = Field(default=None, description="Back sprite URL")


class PokemonCreate(PokemonBase):
    """Schema for creating a Pokemon"""
    pass


class PokemonUpdate(BaseModel):
    """Schema for updating a Pokemon. All fields are optional."""
    name: Optional[str] = Field(default=None, description="Pokemon name")
    height: Optional[float] = Field(default=None, description="Pokemon height")
    weight: Optional[float] = Field(default=None, description="Pokemon weight")
    base_experience: Optional[int] = Field(default=None, description="Base experience")
    types: Optional[List[str]] = Field(default=None, description="Pokemon types (list of names)")
    abilities: Optional[List[str]] = Field(default=None, description="Pokemon abilities (list of names)")
    stats: Optional[Dict[str, int]] = Field(default=None, description="Pokemon stats (name: base_stat)")
    sprite_front: Optional[HttpUrl] = Field(default=None, description="Front sprite URL")
    sprite_back: Optional[HttpUrl] = Field(default=None, description="Back sprite URL")


class PokemonInDB(PokemonBase):
    """Schema for Pokemon in database, includes DB-specific fields"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime


class Pokemon(PokemonInDB):
    """Schema for Pokemon response (often same as InDB)"""
    pass


class PokemonList(BaseModel):
    """Schema for list of Pokemon with pagination"""
    items: List[Pokemon]
    total: int
    page: int = Field(default=1, ge=1)
    size: int = Field(default=10, ge=1, le=100)