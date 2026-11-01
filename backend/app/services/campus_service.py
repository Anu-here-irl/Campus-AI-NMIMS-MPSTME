"""Campus map service handling floor plans, room search, and corridor routing."""

import heapq
from sqlalchemy.orm import Session

from ..models.campus import CampusFloor, CampusRoom, CampusRouteNode, CampusRouteEdge


class CampusService:
    @staticmethod
    def seed_campus_data_if_empty(db: Session):
        """Seed campus floors, rooms, and corridor navigation graph if empty."""
        if db.query(CampusFloor).first():
            return

        # 4 Floors
        floors_data = [
            ("Ground Floor", 0, "assets/maps/floor_0.png"),
            ("First Floor", 1, "assets/maps/floor_1.png"),
            ("Second Floor", 2, "assets/maps/floor_2.png"),
            ("Third Floor", 3, "assets/maps/floor_3.png"),
        ]
        floors = {}
        for name, order, plan_ref in floors_data:
            fl = CampusFloor(floor_name=name, floor_order=order, plan_ref=plan_ref)
            db.add(fl)
            db.flush()
            floors[order] = fl

        # Rooms Data
        rooms_data = [
            # Ground Floor
            (0, "001", "Main Auditorium", "AUDITORIUM", 0.25, 0.40, "Capacity 400 with audio-visual equipment"),
            (0, "002", "Central Library", "LIBRARY", 0.70, 0.35, "Reference books, reading halls, and digital journals"),
            (0, "003", "Cafeteria & Dining Hall", "CAFETERIA", 0.85, 0.80, "Student dining hall"),
            (0, "004", "Administrative Office", "OFFICE", 0.15, 0.20, "Student inquiry, registrar, and fees desk"),
            # MPSTME Ground Floor Verified Rooms from G.jpg
            (0, "E-CR-G1", "Classroom G1 (E CR G1)", "CLASSROOM", 0.15, 0.50, "West Wing smart classroom with dual projectors"),
            (0, "E-CR-G2", "Classroom G2 (E CR G2)", "CLASSROOM", 0.15, 0.35, "West Wing lecture room"),
            (0, "E-CR-G3", "Classroom G3 (E CR G3)", "CLASSROOM", 0.85, 0.30, "East Wing classroom adjoining service corridor"),
            (0, "E-CR-G4", "Classroom G4 (E CR G4)", "CLASSROOM", 0.40, 0.25, "Central classroom facing north corridor"),
            (0, "E-CR-G5", "Classroom G5 (E CR G5)", "CLASSROOM", 0.60, 0.25, "Central classroom facing north corridor"),
            (0, "EXAM-1", "Examination Hall 1 (EXAM 1)", "EXAM", 0.20, 0.25, "West Wing examination & test center"),
            (0, "EXAM-2", "Examination Hall 2 (EXAM 2)", "EXAM", 0.65, 0.05, "North exam hall with internal conference room"),
            (0, "EXAM-3", "Examination Hall 3 (EXAM 3)", "EXAM", 0.85, 0.05, "North-East large examination hall"),
            (0, "LAB-EYANTRA", "e-Yantra Robotics Lab", "LAB", 0.85, 0.15, "IIT Bombay e-Yantra verified robotics research lab"),
            (0, "ATRIUM", "Central Atrium Quadrangle", "COMMON_AREA", 0.50, 0.45, "Multi-story open quadrangle and exhibition space"),
            (0, "ADMISSION-CTR", "Admission Counter & First Aid", "OFFICE", 0.35, 0.70, "Main student admissions window with first aid station"),
            (0, "ADMIN-CABINS", "Administration Cabins 1 to 6", "OFFICE", 0.45, 0.70, "Administrative officer cabins"),
            (0, "LIFTS-A", "North Lift Bank A (Lifts 6-10)", "LIFT", 0.50, 0.15, "5 high-speed passenger lifts (Lifts 6, 7, 8, 9, 10)"),
            (0, "LIFTS-B", "South Lift Bank B (Lifts 1-5)", "LIFT", 0.50, 0.85, "5 high-speed passenger lifts (Lifts 1, 2, 3, 4, 5)"),
            (0, "STAIRS-1", "Staircase No 1 (West Exit)", "STAIRCASE", 0.15, 0.85, "Emergency fire escape stairs to ground exit"),
            (0, "STAIRS-2", "Staircase No 2 (East / LGF)", "STAIRCASE", 0.80, 0.80, "Main staircase connecting to Lower Ground Cafeteria"),
            (0, "STAIRS-4", "Staircase No 4 (North Exit)", "STAIRCASE", 0.50, 0.05, "North emergency exit staircase"),
            (0, "RESTROOM-GIRLS", "Girls Restroom & Diff-Abled", "RESTROOM", 0.15, 0.70, "West wing ladies washroom with accessible booth"),
            (0, "RESTROOM-BOYS", "Boys Restroom & Diff-Abled", "RESTROOM", 0.15, 0.78, "West wing gents washroom with accessible booth"),
            # First Floor
            (1, "101", "Classroom 101", "CLASSROOM", 0.20, 0.30, "Lecture hall for CS / IT students"),
            (1, "102", "Classroom 102", "CLASSROOM", 0.40, 0.30, "Smart classroom with projector"),
            (1, "103", "Computer Lab 1", "LAB", 0.65, 0.50, "60 high-performance workstations"),
            (1, "104", "Faculty Cabin Block A", "FACULTY", 0.85, 0.30, "Faculty consultation rooms"),
            # Second Floor
            (2, "201", "Classroom 201", "CLASSROOM", 0.20, 0.30, "Lecture hall"),
            (2, "204", "Classroom 204", "CLASSROOM", 0.45, 0.50, "Smart Lecture Theater - Exam & Class Hall"),
            (2, "205", "Computer Lab 2 (AI/NLP Lab)", "LAB", 0.65, 0.50, "GPU-enabled Deep Learning & NLP laboratory"),
            (2, "206", "Computer Lab 3 (Networks Lab)", "LAB", 0.80, 0.50, "Cisco routing and networks laboratory"),
            # Third Floor
            (3, "301", "Seminar Hall", "SEMINAR", 0.30, 0.40, "Conference & guest lecture hall with acoustic panels"),
            (3, "302", "Project & Robotics Lab", "LAB", 0.60, 0.45, "Embedded systems, IoT, and robotics workshop"),
            (3, "303", "MBA Block Room 101", "CLASSROOM", 0.80, 0.40, "Postgraduate executive classroom"),
        ]

        for fl_order, code, name, rtype, x, y, details in rooms_data:
            room = CampusRoom(
                floor_id=floors[fl_order].id,
                room_code=code,
                room_name=name,
                room_type=rtype,
                map_x=x,
                map_y=y,
                details=details,
            )
            db.add(room)

        # Basic corridor route nodes for floor 2 (sample routing demo)
        n1 = CampusRouteNode(floor_id=floors[2].id, x=0.20, y=0.50, node_type="CORRIDOR")
        n2 = CampusRouteNode(floor_id=floors[2].id, x=0.45, y=0.50, node_type="ROOM_DOOR") # Door to 204
        n3 = CampusRouteNode(floor_id=floors[2].id, x=0.65, y=0.50, node_type="ROOM_DOOR") # Door to Lab 2
        n4 = CampusRouteNode(floor_id=floors[2].id, x=0.80, y=0.50, node_type="ROOM_DOOR") # Door to Lab 3
        db.add_all([n1, n2, n3, n4])
        db.flush()

        db.add(CampusRouteEdge(from_node_id=n1.id, to_node_id=n2.id, distance=15.0))
        db.add(CampusRouteEdge(from_node_id=n2.id, to_node_id=n1.id, distance=15.0))
        db.add(CampusRouteEdge(from_node_id=n2.id, to_node_id=n3.id, distance=12.0))
        db.add(CampusRouteEdge(from_node_id=n3.id, to_node_id=n2.id, distance=12.0))
        db.add(CampusRouteEdge(from_node_id=n3.id, to_node_id=n4.id, distance=10.0))
        db.add(CampusRouteEdge(from_node_id=n4.id, to_node_id=n3.id, distance=10.0))

        db.commit()

    @staticmethod
    def list_floors(db: Session) -> list[CampusFloor]:
        CampusService.seed_campus_data_if_empty(db)
        return db.query(CampusFloor).order_by(CampusFloor.floor_order.asc()).all()

    @staticmethod
    def search_rooms(db: Session, query: str) -> list[CampusRoom]:
        CampusService.seed_campus_data_if_empty(db)
        term = f"%{query}%"
        return (
            db.query(CampusRoom)
            .filter((CampusRoom.room_code.ilike(term)) | (CampusRoom.room_name.ilike(term)) | (CampusRoom.details.ilike(term)))
            .all()
        )

    @classmethod
    def _resolve_room(cls, db: Session, code_or_name: str) -> CampusRoom | None:
        """Resolve a room entity by exact code, stripped prefix, or descriptive name."""
        import math
        import re

        target = code_or_name.strip()
        if not target:
            return None

        # 1. Exact match on room_code
        room = db.query(CampusRoom).filter(CampusRoom.room_code.ilike(target)).first()
        if room:
            return room

        # 2. Match without "Room", "Lab", "Hall" prefix e.g. "Room 204" -> "204"
        clean_code = re.sub(r"(?i)\b(?:room|lab|classroom|hall|theater)\b", "", target).strip()
        if clean_code:
            room = db.query(CampusRoom).filter(CampusRoom.room_code.ilike(clean_code)).first()
            if room:
                return room

        # 3. Fuzzy / partial match on room_name or room_code
        room = db.query(CampusRoom).filter(CampusRoom.room_name.ilike(f"%{target}%")).first()
        if room:
            return room

        return None

    @staticmethod
    def find_route(db: Session, from_code: str, to_code: str) -> dict | None:
        """Find navigation directions and corridor route steps between two rooms."""
        import math

        CampusService.seed_campus_data_if_empty(db)
        r_from = CampusService._resolve_room(db, from_code)
        r_to = CampusService._resolve_room(db, to_code)

        if not r_from or not r_to:
            return None

        from_floor = r_from.floor
        to_floor = r_to.floor
        from_floor_order = from_floor.floor_order if from_floor else 0
        to_floor_order = to_floor.floor_order if to_floor else 0

        steps = []
        nodes = []

        if from_floor_order == to_floor_order:
            # Same floor corridor navigation
            dx = (r_to.map_x or 0.5) - (r_from.map_x or 0.2)
            dy = (r_to.map_y or 0.5) - (r_from.map_y or 0.5)
            euc_dist = math.sqrt(dx * dx + dy * dy)
            corridor_dist = max(10.0, round(euc_dist * 60.0, 1))

            direction_hint = "East Wing (Right)" if dx >= 0 else "West Wing (Left)"

            steps.append({
                "instruction": f"Exit {r_from.room_name} ({r_from.room_code}) and enter the {from_floor.floor_name} main corridor.",
                "distance": 5.0,
            })
            steps.append({
                "instruction": f"Walk {corridor_dist}m along the corridor towards the {direction_hint}.",
                "distance": corridor_dist,
            })
            steps.append({
                "instruction": f"Arrive at destination: {r_to.room_name} ({r_to.room_code}).",
                "distance": 3.0,
            })
            total = round(5.0 + corridor_dist + 3.0, 1)

            nodes = [
                {"x": r_from.map_x or 0.2, "y": r_from.map_y or 0.5, "floor": from_floor_order},
                {"x": (r_from.map_x or 0.2 + r_to.map_x or 0.6) / 2.0, "y": 0.5, "floor": from_floor_order},
                {"x": r_to.map_x or 0.6, "y": r_to.map_y or 0.5, "floor": to_floor_order},
            ]
        else:
            # Inter-floor vertical navigation
            floor_diff = to_floor_order - from_floor_order
            action = "Ascend" if floor_diff > 0 else "Descend"
            vertical_dist = round(abs(floor_diff) * 15.0, 1)

            dist_to_stairs = max(8.0, round(abs((r_from.map_x or 0.2) - 0.50) * 50.0 + 8.0, 1))
            dist_from_stairs = max(8.0, round(abs((r_to.map_x or 0.6) - 0.50) * 50.0 + 8.0, 1))

            steps.append({
                "instruction": f"Exit {r_from.room_name} ({r_from.room_code}) on {from_floor.floor_name} and walk {dist_to_stairs}m to the Central Stairs / Elevator.",
                "distance": dist_to_stairs,
            })
            steps.append({
                "instruction": f"{action} {abs(floor_diff)} floor(s) via Central Stairs / Elevator to {to_floor.floor_name}.",
                "distance": vertical_dist,
            })
            steps.append({
                "instruction": f"Exit onto {to_floor.floor_name} corridor and proceed {dist_from_stairs}m towards {r_to.room_name}.",
                "distance": dist_from_stairs,
            })
            steps.append({
                "instruction": f"Arrive at destination: {r_to.room_name} ({r_to.room_code}).",
                "distance": 3.0,
            })
            total = round(dist_to_stairs + vertical_dist + dist_from_stairs + 3.0, 1)

            nodes = [
                {"x": r_from.map_x or 0.2, "y": r_from.map_y or 0.5, "floor": from_floor_order},
                {"x": 0.50, "y": 0.50, "floor": from_floor_order, "type": "STAIRS"},
                {"x": 0.50, "y": 0.50, "floor": to_floor_order, "type": "STAIRS"},
                {"x": r_to.map_x or 0.6, "y": r_to.map_y or 0.5, "floor": to_floor_order},
            ]

        return {
            "from_room": r_from.room_name,
            "to_room": r_to.room_name,
            "total_distance": total,
            "steps": steps,
            "nodes": nodes,
        }


campus_service = CampusService()
