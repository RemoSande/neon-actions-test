import httpx
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.config import settings
from app.models.pokemon import Pokemon
from app.schemas.pokemon import PokemonCreate, PokemonBase


class PokemonService:
    """Service for fetching and managing Pokemon data"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.base_url = settings.pokemon_api_base_url
    
    async def fetch_pokemon_from_api(self, pokemon_id: int) -> Optional[Dict[str, Any]]:
        """Fetch Pokemon data from PokeAPI"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/pokemon/{pokemon_id}")
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError:
                return None
            except httpx.RequestError:
                return None
    
    def parse_pokemon_data(self, data: Dict[str, Any]) -> PokemonCreate:
        """Parse raw Pokemon data into our PokemonCreate schema"""
        types = [t["type"]["name"] for t in data.get("types", [])]
        abilities = [a["ability"]["name"] for a in data.get("abilities", [])]
        stats = {
            stat["stat"]["name"]: stat["base_stat"] 
            for stat in data.get("stats", [])
        }
        sprites = data.get("sprites", {})
        
        return PokemonCreate(
            pokemon_id=data["id"],
            name=data.get("name", "Unknown").lower(),
            height=data.get("height", 0) / 10,
            weight=data.get("weight", 0) / 10,
            base_experience=data.get("base_experience", 0),
            types=types,
            abilities=abilities,
            stats=stats,
            sprite_front=sprites.get("front_default"),
            sprite_back=sprites.get("back_default"),
        )
    
    async def get_or_fetch_pokemon(self, pokemon_id: int) -> Optional[Pokemon]:
        """Get Pokemon from DB or fetch from API if not found, then store."""
        result = await self.db.execute(
            select(Pokemon).where(Pokemon.pokemon_id == pokemon_id)
        )
        pokemon = result.scalar_one_or_none()
        
        if pokemon:
            return pokemon
        
        api_data = await self.fetch_pokemon_from_api(pokemon_id)
        if not api_data:
            return None
        
        pokemon_create_data = self.parse_pokemon_data(api_data)
        
        new_pokemon = Pokemon(**pokemon_create_data.model_dump())
        self.db.add(new_pokemon)
        await self.db.commit()
        await self.db.refresh(new_pokemon)
        return new_pokemon

    async def fetch_and_upsert_pokemon(self, pokemon_id: int) -> Optional[Pokemon]:
        """Force fetch Pokemon from API and update or create in DB."""
        api_data = await self.fetch_pokemon_from_api(pokemon_id)
        if not api_data:
            return None

        parsed_data = self.parse_pokemon_data(api_data)

        result = await self.db.execute(
            select(Pokemon).where(Pokemon.pokemon_id == pokemon_id)
        )
        existing_pokemon = result.scalar_one_or_none()

        if existing_pokemon:
            update_values = parsed_data.model_dump(exclude_unset=True)
            for key, value in update_values.items():
                if hasattr(existing_pokemon, key):
                    setattr(existing_pokemon, key, value)
            self.db.add(existing_pokemon)
            pokemon_to_return = existing_pokemon
        else:
            pokemon_to_return = Pokemon(**parsed_data.model_dump())
            self.db.add(pokemon_to_return)
        
        await self.db.commit()
        await self.db.refresh(pokemon_to_return)
        return pokemon_to_return

    async def get_pokemon_list(
        self, 
        skip: int = 0, 
        limit: int = 10
    ) -> tuple[List[Pokemon], int]:
        """Get list of Pokemon from database with total count."""
        total_result = await self.db.execute(select(func.count(Pokemon.id)))
        total = total_result.scalar_one_or_none() or 0

        if total == 0:
            return [], 0
            
        list_result = await self.db.execute(
            select(Pokemon).offset(skip).limit(limit)
        )
        pokemon_list = list_result.scalars().all()
        
        return list(pokemon_list), total
    
    async def search_pokemon_by_name(self, name: str) -> Optional[Pokemon]:
        """Search for a Pokemon by name (case-insensitive)."""
        result = await self.db.execute(
            select(Pokemon).where(Pokemon.name == name.lower())
        )
        return result.scalar_one_or_none()