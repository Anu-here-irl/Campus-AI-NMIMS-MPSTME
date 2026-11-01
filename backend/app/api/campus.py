"""Indoor Campus Map and Routing API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.campus import CampusFloor, CampusRoom
from ..schemas.campus import CampusFloorResponse, CampusRoomResponse, RouteResponse
from ..services.campus_service import campus_service

router = APIRouter(prefix="/campus", tags=["Indoor Campus Map"])


@router.get("/floors", response_model=list[CampusFloorResponse])
def get_floors(db: Session = Depends(get_db)):
    """Retrieve all college floors with their rooms and layout references."""
    return campus_service.list_floors(db)


@router.get("/floors/{id}/rooms", response_model=list[CampusRoomResponse])
def get_rooms_by_floor(id: int, db: Session = Depends(get_db)):
    """Retrieve all rooms on a specific floor."""
    floor = db.query(CampusFloor).filter(CampusFloor.id == id).first()
    if not floor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Floor not found.")
    return floor.rooms


@router.get("/search", response_model=list[CampusRoomResponse])
def search_rooms(
    q: str = Query(..., min_length=1, description="Search term (room code, name, type)"),
    db: Session = Depends(get_db),
):
    """Search for campus rooms, labs, auditoriums, and facilities."""
    return campus_service.search_rooms(db, q)


@router.get("/routes", response_model=RouteResponse)
def get_route_between_rooms(
    from_room: str = Query(..., description="Starting room code (e.g. 101)"),
    to_room: str = Query(..., description="Destination room code (e.g. 204)"),
    db: Session = Depends(get_db),
):
    """Get corridor navigation steps and directions between two campus locations."""
    route = campus_service.find_route(db, from_room, to_room)
    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not compute route between '{from_room}' and '{to_room}'. One or both locations were not found.",
        )
    return route
