import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pokemon import Pokemon
from app.services.pokemon import PokemonService


def test_get_pokemon_not_found(client: TestClient):
    """Test getting a Pokemon that doesn't exist"""
    response = client.get("/api/v1/pokemon/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_list_pokemon_empty(client: TestClient):
    """Test listing Pokemon when database is empty"""
    response = client.get("/api/v1/pokemon/")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["page"] == 1
    assert data["size"] == 10


def test_list_pokemon_pagination(client: TestClient):
    """Test pagination parameters"""
    response = client.get("/api/v1/pokemon/?page=2&size=20")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2
    assert data["size"] == 20


@pytest.mark.asyncio
async def test_pokemon_service_fetch(db_session: AsyncSession):
    """Test Pokemon service fetching logic"""
    service = PokemonService(db_session)
    
    # Mock the API call
    mock_api_data = {
        "id": 1,
        "name": "bulbasaur",
        "height": 7,
        "weight": 69,
        "base_experience": 64,
        "types": [{"slot": 1, "type": {"name": "grass"}}],
        "abilities": [{"slot": 1, "ability": {"name": "overgrow"}, "is_hidden": False}],
        "stats": [{"stat": {"name": "hp"}, "base_stat": 45, "effort": 0}],
        "sprites": {"front_default": "https://example.com/sprite.png", "back_default": None}
    }
    
    # Test parsing
    parsed_data = service.parse_pokemon_data(mock_api_data)
    assert parsed_data.pokemon_id == 1
    assert parsed_data.name == "bulbasaur"
    assert parsed_data.height == 0.7  # Converted to meters
    assert parsed_data.weight == 6.9  # Converted to kg
    assert "grass" in parsed_data.types
    assert "overgrow" in parsed_data.abilities
    assert parsed_data.stats["hp"] == 45


def test_search_pokemon_not_found(client: TestClient):
    """Test searching for a Pokemon that doesn't exist"""
    response = client.get("/api/v1/pokemon/search/unknown")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()