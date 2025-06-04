from sqlalchemy import String, Integer, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin
from typing import List, Dict


class Pokemon(Base, TimestampMixin):
    """Pokemon model for storing Pokemon data"""
    __tablename__ = "pokemon"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pokemon_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    height: Mapped[float] = mapped_column(Float, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    base_experience: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Store types as JSON array of strings
    types: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    
    # Store abilities as JSON array of strings
    abilities: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    
    # Store stats as JSON object (string keys, integer values)
    stats: Mapped[Dict[str, int]] = mapped_column(JSON, nullable=False)
    
    # Store sprite URLs
    sprite_front: Mapped[str] = mapped_column(String(500), nullable=True)
    sprite_back: Mapped[str] = mapped_column(String(500), nullable=True)
    
    def __repr__(self) -> str:
        return f"<Pokemon(id={self.id}, name={self.name}, pokemon_id={self.pokemon_id})>"