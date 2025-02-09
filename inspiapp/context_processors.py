import os
from dotenv import load_dotenv


def header_app(request) -> dict:
    current_path = request.path

    # get string before first /
    module_name: str = current_path.split("/")[1]

    local_env: bool = os.getenv("LOCAL", "False") == "True"

    base_url: str = "http://localhost:8000"

    header_app = [
        {
            "display_name_short": "DPV Tool",
            "display_name": "Alle DPV Tools",
            "main_url": f"{base_url}",
            "icon_name": "brain",
            "module_name": "",
            "description": "Hier findest du viele Tools für Pfadfinder.",
            "inspi_img": "inspi_science.webp",
            "domain": "https://dpvonline.cloud",
            "icon": "images/inspi_thinking.webp",
            "is_visible": False,
        },
        {
            "display_name_short": "Idee",
            "display_name": "Gruppenstunden Ideen",
            "main_url": f"{base_url}/activity/",
            "icon_name": "brain",
            "module_name": "activity",
            "description": "Hier findest du viele Ideen für deine Gruppenstunden.",
            "inspi_img": "inspi_science.webp",
            "domain": "https://gruppenstunde.de",
            "icon": "images/inspi_thinking.webp",
            "is_visible": True,
        },
        {
            "display_name_short": "Essen",
            "display_name": "Essensplaner",
            "main_url": f"{base_url}/food/main",
            "icon_name": "euro",
            "module_name": "food",
            "description": "Hier kannst du deinen Essensplaner verwalten.",
            "inspi_img": "inspi_food.webp",
            "domain": "https://gruppenstunde.de",
            "icon": "images/inspi_thinking.webp",
            "is_visible": True,
        },
        {
            "display_name_short": "Wissen",
            "display_name": "Pfadfinderwissen",
            "main_url": f"{base_url}/blog/home",
            "icon_name": "question",
            "module_name": "blog",
            "description": "Hier findest du viele Informationen über die Pfadfinder.",
            "inspi_img": "inspi_flying.webp",
            "domain": "https://gruppenstunde.de",
            "icon": "images/inspi_thinking.webp",
            "is_visible": True,
        },
        {
            "display_name_short": "Gruppen",
            "display_name": "Gruppenverwaltung",
            "main_url": f"{base_url}/group/dashboard",
            "icon_name": "user-plus",
            "module_name": "group",
            "description": "Hier kannst du deine Gruppen verwalten.",
            "inspi_img": "inspi_backpack.webp",
            "domain": "https://gruppenstunde.de",
            "icon": "images/logo.png",
            "is_visible": True,
        },
        {
            "display_name_short": "Anmeldung",
            "display_name": "Anmelde-Tool",
            "main_url": f"{base_url}/event/basic",
            "icon_name": "plus",
            "module_name": "event",
            "description": "Hier kannst du deine Anmeldungen verwalten.",
            "inspi_img": "inspi_teacher.webp",
            "domain": "https://gruppenstunde.de",
            "icon": "images/logo.png",
            "is_visible": True,
        },
    ]

    try:
        current_app = [app for app in header_app if app["module_name"] == module_name][
            0
        ]
    except IndexError:
        current_app = header_app[0]

     # filter is_visible
    header_app = [app for app in header_app if app["is_visible"]]


    return {
        "header_app": header_app,
        "current_app": current_app,
        "is_local": local_env,
    }
