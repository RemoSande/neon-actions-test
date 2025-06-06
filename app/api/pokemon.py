from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from app.db.session import DbSession
from app.schemas.pokemon import Pokemon, PokemonList
from app.services.pokemon import PokemonService

router = APIRouter(prefix="/pokemon", tags=["pokemon"])


@router.get("/{pokemon_id}", response_model=Pokemon)
async def get_pokemon(
    db: DbSession,
    pokemon_id: int,
) -> Pokemon:
    """
    Get a Pokemon by ID.
    
    If the Pokemon doesn't exist in the database, it will be fetched
    from the PokeAPI and stored for future use.
    """
    service = PokemonService(db)    
    pokemon = await service.get_or_fetch_pokemon(pokemon_id)
    
    if not pokemon:
        raise HTTPException(
            status_code=404,
            detail=f"Pokemon with ID {pokemon_id} not found in DB or PokeAPI"
        )
    
    return pokemon


@router.get("/", response_model=PokemonList)
async def list_pokemon(
    db: DbSession,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
) -> PokemonList:
    """
    List Pokemon with pagination.
    
    Only returns Pokemon that have been previously fetched and stored
    in the database.
    """
    service = PokemonService(db)
    skip = (page - 1) * size
    
    pokemon_list, total = await service.get_pokemon_list(skip=skip, limit=size)
    
    return PokemonList(
        items=pokemon_list,
        total=total,
        page=page,
        size=size
    )


@router.get("/search/{name}", response_model=Pokemon)
async def search_pokemon(
    name: str,
    db: DbSession
) -> Pokemon:
    """
    Search for a Pokemon by name in the local database (case-insensitive).
    Name should be the exact Pokemon name.
    """
    service = PokemonService(db)
    pokemon = await service.search_pokemon_by_name(name)
    
    if not pokemon:
        raise HTTPException(
            status_code=404,
            detail=f"Pokemon with name '{name}' not found in database. Try fetching it first if it exists in PokeAPI."
        )
    
    return pokemon


@router.post("/fetch/{pokemon_id}", response_model=Pokemon)
async def fetch_and_store_pokemon(
    pokemon_id: int,
    db: DbSession
) -> Pokemon:
    """
    Explicitly fetch a Pokemon from PokeAPI and store/update it in the database.
    
    This endpoint forces a fetch from the PokeAPI. If the Pokemon
    already exists in the database, it will be updated with the new data.
    If not, it will be created.
    """
    service = PokemonService(db)
    
    pokemon = await service.fetch_and_upsert_pokemon(pokemon_id)
    
    if not pokemon:
        # This case occurs if fetch_pokemon_from_api in the service returned None
        raise HTTPException(
            status_code=404,
            detail=f"Pokemon with ID {pokemon_id} not found in PokeAPI, or an error occurred during fetching."
        )
    
    return pokemon