"""Generator for clean, unjumbled, aligned campus floor plans for SVKM's NMIMS MPSTME."""

import json
import os

def create_standard_floor(floor_id: str, floor_order: int, floor_name: str, plan_image: str):
    prefix = floor_id
    floor_num = floor_id
    
    # West Wing Classrooms (x: 60, width: 220)
    cr_w1 = {"code": f"CR-{floor_num}01", "name": f"Lecture Hall {floor_num}01", "category": "CLASSROOM", "x": 60, "y": 200, "width": 220, "height": 130, "verified": True, "notes": f"Floor {floor_num} West smart classroom"}
    cr_w2 = {"code": f"CR-{floor_num}02", "name": f"Lecture Hall {floor_num}02", "category": "CLASSROOM", "x": 60, "y": 350, "width": 220, "height": 130, "verified": True, "notes": f"Floor {floor_num} West smart classroom"}
    cr_w3 = {"code": f"CR-{floor_num}03", "name": f"Lecture Hall {floor_num}03", "category": "CLASSROOM", "x": 60, "y": 500, "width": 220, "height": 130, "verified": True, "notes": f"Floor {floor_num} West smart classroom"}
    restroom_w = {"code": f"RESTROOM-{floor_num}", "name": "Restrooms (M/F)", "category": "RESTROOM", "x": 60, "y": 660, "width": 220, "height": 90, "verified": True, "notes": "Accessible washrooms"}
    stairs_1 = {"code": f"STAIRS-1-F{floor_num}", "name": "Staircase 1 (West Exit)", "category": "STAIRCASE", "x": 60, "y": 770, "width": 140, "height": 70, "verified": True, "notes": "West emergency fire escape"}

    # Central Core (x: 310..690)
    stairs_4 = {"code": f"STAIRS-4-F{floor_num}", "name": "Staircase 4 (North)", "category": "STAIRCASE", "x": 480, "y": 40, "width": 90, "height": 70, "verified": True, "notes": "North emergency stairs"}
    lifts_a = {"code": f"LIFTS-{floor_num}-A", "name": f"Lifts 6-10 (North Bank)", "category": "LIFT", "x": 350, "y": 130, "width": 270, "height": 50, "verified": True, "notes": "North high-speed elevator bank"}
    
    cr_c1 = {"code": f"CR-{floor_num}04", "name": f"Smart Classroom {floor_num}04", "category": "CLASSROOM", "x": 310, "y": 200, "width": 175, "height": 130, "verified": True, "notes": f"Center-North classroom {floor_num}04"}
    cr_c2 = {"code": f"CR-{floor_num}05", "name": f"Smart Classroom {floor_num}05", "category": "CLASSROOM", "x": 515, "y": 200, "width": 175, "height": 130, "verified": True, "notes": f"Center-North classroom {floor_num}05"}
    
    atrium = {"code": f"ATRIUM-{floor_num}", "name": f"Central Atrium Gallery (F{floor_num})", "category": "COMMON_AREA", "x": 310, "y": 350, "width": 380, "height": 240, "verified": True, "notes": "Open multi-floor quadrangle view"}
    
    cr_c3 = {"code": f"CR-{floor_num}06", "name": f"Tutorial Room {floor_num}06", "category": "CLASSROOM", "x": 310, "y": 610, "width": 175, "height": 120, "verified": True, "notes": f"Center-South tutorial room {floor_num}06"}
    cr_c4 = {"code": f"CR-{floor_num}07", "name": f"Seminar Room {floor_num}07", "category": "CLASSROOM", "x": 515, "y": 610, "width": 175, "height": 120, "verified": True, "notes": f"Center-South seminar room {floor_num}07"}
    
    lifts_b = {"code": f"LIFTS-{floor_num}-B", "name": f"Lifts 1-5 (South Bank)", "category": "LIFT", "x": 350, "y": 750, "width": 270, "height": 50, "verified": True, "notes": "South high-speed elevator bank"}
    stairs_2 = {"code": f"STAIRS-2-F{floor_num}", "name": "Staircase 2 (Central)", "category": "STAIRCASE", "x": 480, "y": 820, "width": 100, "height": 65, "verified": True, "notes": "Main internal staircase"}

    # East Wing (x: 720, width: 220)
    cl_e1 = {"code": f"CL-{floor_num}01", "name": f"Computer Lab {floor_num}01", "category": "LAB", "x": 720, "y": 200, "width": 220, "height": 130, "verified": True, "notes": f"Department computing laboratory {floor_num}01"}
    cl_e2 = {"code": f"CL-{floor_num}02", "name": f"Research Lab {floor_num}02", "category": "LAB", "x": 720, "y": 350, "width": 220, "height": 130, "verified": True, "notes": f"AI, ML & Advanced Research Lab {floor_num}02"}
    
    lift_svc = {"code": f"LIFT-SVC-F{floor_num}", "name": "Service Elevator", "category": "LIFT", "x": 720, "y": 500, "width": 45, "height": 60, "verified": True, "notes": "Goods & service lift"}
    stairs_3 = {"code": f"STAIRS-3-F{floor_num}", "name": "Staircase 3 (East Wing)", "category": "STAIRCASE", "x": 780, "y": 500, "width": 110, "height": 60, "verified": True, "notes": "East corridor staircase"}
    
    faculty_1 = {"code": f"FACULTY-{floor_num}01", "name": f"Faculty Cabins {floor_num}01", "category": "OFFICE", "x": 720, "y": 580, "width": 220, "height": 120, "verified": True, "notes": f"Faculty chambers and consultation cabins"}
    dept_off = {"code": f"DEPT-{floor_num}02", "name": f"Department Office {floor_num}", "category": "OFFICE", "x": 720, "y": 720, "width": 220, "height": 110, "verified": True, "notes": f"HOD executive chamber & secretariat"}

    rooms = [
        cr_w1, cr_w2, cr_w3, restroom_w, stairs_1,
        stairs_4, lifts_a, cr_c1, cr_c2, atrium, cr_c3, cr_c4, lifts_b, stairs_2,
        cl_e1, cl_e2, lift_svc, stairs_3, faculty_1, dept_off
    ]

    return {
        "floor_id": floor_id,
        "floor_order": floor_order,
        "floor_name": floor_name,
        "plan_image": plan_image,
        "width": 1000,
        "height": 1100,
        "rooms": rooms
    }

# Ground Floor with cleaned, perfectly aligned non-overlapping coordinates
ground_floor = {
    "floor_id": "G",
    "floor_order": 0,
    "floor_name": "Ground Floor",
    "plan_image": "G.jpg",
    "width": 1000,
    "height": 1150,
    "rooms": [
        # West Wing
        {"code": "LIBRARY", "name": "Central Library & Digital Repository", "category": "COMMON_AREA", "x": 60, "y": 200, "width": 220, "height": 150, "verified": True, "notes": "Main library, open 8:30 AM to 8:00 PM"},
        {"code": "E-CR-G1", "name": "Classroom G1 (E CR G1)", "category": "CLASSROOM", "x": 60, "y": 370, "width": 220, "height": 130, "verified": True, "notes": "West Wing smart classroom"},
        {"code": "E-CR-G2", "name": "Classroom G2 (E CR G2)", "category": "CLASSROOM", "x": 60, "y": 520, "width": 220, "height": 130, "verified": True, "notes": "West Wing lecture hall"},
        {"code": "RESTROOM-G", "name": "Restrooms & Diff-Abled", "category": "RESTROOM", "x": 60, "y": 670, "width": 220, "height": 90, "verified": True, "notes": "Accessible washrooms"},
        {"code": "STAIRS-1", "name": "Staircase 1 (West Exit)", "category": "STAIRCASE", "x": 60, "y": 780, "width": 140, "height": 70, "verified": True, "notes": "Emergency fire escape exit"},

        # Central Core
        {"code": "STAIRS-4", "name": "North Exit Staircase", "category": "STAIRCASE", "x": 480, "y": 40, "width": 90, "height": 70, "verified": True, "notes": "North emergency exit"},
        {"code": "LIFTS-A", "name": "North Lift Bank A (Lifts 6-10)", "category": "LIFT", "x": 350, "y": 130, "width": 270, "height": 50, "verified": True, "notes": "5 passenger elevators"},
        {"code": "E-CR-G4", "name": "Classroom G4 (E CR G4)", "category": "CLASSROOM", "x": 310, "y": 200, "width": 175, "height": 130, "verified": True, "notes": "Central classroom"},
        {"code": "E-CR-G5", "name": "Classroom G5 (E CR G5)", "category": "CLASSROOM", "x": 515, "y": 200, "width": 175, "height": 130, "verified": True, "notes": "Central classroom"},
        {"code": "ATRIUM", "name": "Central Atrium Quadrangle", "category": "COMMON_AREA", "x": 310, "y": 350, "width": 380, "height": 240, "verified": True, "notes": "Main quadrangle & exhibition space"},
        {"code": "ADMIN-RECEPTION", "name": "Admin Reception & Helpdesk", "category": "OFFICE", "x": 310, "y": 610, "width": 175, "height": 110, "verified": True, "notes": "Visitor reception & student services"},
        {"code": "ADMIN-CABINS", "name": "Administration & Admissions", "category": "OFFICE", "x": 515, "y": 610, "width": 175, "height": 110, "verified": True, "notes": "Academic & admissions offices"},
        {"code": "LIFTS-B", "name": "South Lift Bank B (Lifts 1-5)", "category": "LIFT", "x": 350, "y": 740, "width": 270, "height": 50, "verified": True, "notes": "5 passenger elevators"},
        {"code": "MAIN-FOYER", "name": "Main Entrance Foyer", "category": "COMMON_AREA", "x": 310, "y": 810, "width": 380, "height": 70, "verified": True, "notes": "Main college entry from campus gates"},

        # East Wing
        {"code": "AUDITORIUM", "name": "Main Auditorium (Room 001)", "category": "COMMON_AREA", "x": 720, "y": 200, "width": 220, "height": 180, "verified": True, "notes": "Main large acoustic auditorium & stage"},
        {"code": "LAB-EYANTRA", "name": "e-Yantra Robotics Research Lab", "category": "LAB", "x": 720, "y": 400, "width": 220, "height": 120, "verified": True, "notes": "IIT Bombay robotics laboratory"},
        {"code": "STAIRS-3", "name": "Staircase 3 (East)", "category": "STAIRCASE", "x": 780, "y": 540, "width": 110, "height": 60, "verified": True, "notes": "East corridor staircase"},
        {"code": "MEETING-1", "name": "Executive Conference Hall", "category": "OFFICE", "x": 720, "y": 620, "width": 220, "height": 120, "verified": True, "notes": "Boardroom & executive meetings"},
        {"code": "SERVER-ROOM", "name": "Central IT & Server Room", "category": "UTILITY", "x": 720, "y": 760, "width": 220, "height": 90, "verified": True, "notes": "Core networking & data center"}
    ]
}

# Lower Ground Floor
lg_floor = {
    "floor_id": "LG",
    "floor_order": -1,
    "floor_name": "Lower Ground Floor",
    "plan_image": "LG.jpg",
    "width": 1000,
    "height": 900,
    "rooms": [
        {"code": "AUDITORIUM-SM", "name": "Small Auditorium (Seminar Hall)", "category": "COMMON_AREA", "x": 60, "y": 200, "width": 220, "height": 220, "verified": True, "notes": "Acoustic seminar theater"},
        {"code": "E-CR-LG1", "name": "Classroom LG 1", "category": "CLASSROOM", "x": 60, "y": 440, "width": 220, "height": 150, "verified": True, "notes": "Lower ground lecture hall"},
        {"code": "CAFETERIA", "name": "Central Student Cafeteria & Food Court", "category": "COMMON_AREA", "x": 310, "y": 200, "width": 380, "height": 280, "verified": True, "notes": "Main student dining facility"},
        {"code": "FACULTY-DINING", "name": "Faculty Dining Area", "category": "COMMON_AREA", "x": 310, "y": 500, "width": 180, "height": 120, "verified": True, "notes": "Staff dining hall"},
        {"code": "STUDENT-COUNCIL", "name": "Student Council Headquarters", "category": "OFFICE", "x": 510, "y": 500, "width": 180, "height": 120, "verified": True, "notes": "Student committee & club rooms"},
        {"code": "BIG-SEMINAR", "name": "Big Seminar Hall & Exhibition", "category": "COMMON_AREA", "x": 720, "y": 200, "width": 220, "height": 260, "verified": True, "notes": "Multipurpose seminar and event hall"},
        {"code": "ELEC-PANEL", "name": "Electrical & Substation Control", "category": "UTILITY", "x": 720, "y": 480, "width": 220, "height": 140, "verified": True, "notes": "Main electrical panels"},
        {"code": "LIFTS-LG-NORTH", "name": "Lifts 6-10 (North Bank)", "category": "LIFT", "x": 350, "y": 120, "width": 270, "height": 50, "verified": True, "notes": "Elevators to Floors 1-8"},
        {"code": "LIFTS-LG-SOUTH", "name": "Lifts 1-5 (South Bank)", "category": "LIFT", "x": 350, "y": 640, "width": 270, "height": 50, "verified": True, "notes": "Elevators to Floors 1-8"}
    ]
}

floors = [lg_floor, ground_floor]
for i in range(1, 9):
    floors.append(create_standard_floor(str(i), i, f"Floor {i}", f"{i}.jpg"))

campus_manifest = {
    "campus_name": "SVKM's NMIMS - MPSTME",
    "location": "Irla, Vile Parle (W), Mumbai",
    "floors": floors
}

target_file = 'CAMPUS AI/android-app/app/src/main/assets/campus_floors.json'
os.makedirs(os.path.dirname(target_file), exist_ok=True)
with open(target_file, 'w', encoding='utf-8') as f:
    json.dump(campus_manifest, f, indent=2)

print(f"Generated clean campus manifest for {len(floors)} floors at {target_file}")
