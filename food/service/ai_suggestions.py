from django.shortcuts import get_object_or_404
from food.models import Ingredient, RetailSection, NutritionalTag
from pydantic import BaseModel, Field
from typing import List, Optional
from activity.activity.service.admin.ai_suggestion import get_ai_suggestion


def get_suggestions_for_step(step_name, ingredient_slug):
    """
    Get AI suggestions for a specific wizard step
    """
    ingredient = get_object_or_404(Ingredient, slug=ingredient_slug)
    
    # Select the appropriate output model and prompt based on the wizard step
    if step_name == "basic_info":
        return get_basic_info_suggestions(ingredient)
    elif step_name == "physical_properties":
        return get_physical_properties_suggestions(ingredient)
    elif step_name == "nutritional_tags":
        return get_nutritional_tags_suggestions(ingredient)
    elif step_name == "scores":
        return get_scores_suggestions(ingredient)
    elif step_name == "recipe_info":
        return get_recipe_info_suggestions(ingredient)
    elif step_name == "nutrition":
        return get_nutrition_suggestions(ingredient)
    
    # Default case if no specific handler
    return {}


def get_basic_info_suggestions(ingredient):
    """Get suggestions for basic information step"""
    retail_sections = RetailSection.objects.all()
    retail_sections_list = [section.name for section in retail_sections]

    class OutputModel(BaseModel):
        name: str = Field(
            min_length=5,
            max_length=1000,
            description="name der Zutat. Kurz und prägnant. Ohne Mengenangaben. Ohne Sonderzeichen. Ohne Werbung. Ohne Markennamen.",
        )
        description: str = Field(
            min_length=5,
            max_length=1000,
            description="Beschreibung der Zutat. Kurz und prägnant. Ohne Mengenangaben und Einheiten. Ohne Sonderzeichen.",
        )
        retail_section: str = Field(
            description=f"Einzelhandelsbereich der Zutat. Z.B. {', '.join(retail_sections_list)}",
        )

    output = get_ai_suggestion(
        prompt=f"""
            Gebe mir passende technisch genaue Texte für die Rezepzutat
            ohne Werbung. Sehr sachlich. Kurz. Konkret.
            Entferne alle Mengenangaben und Einheiten. Ohne Markennamen.
            {ingredient.name} {ingredient.description}
        """,
        model="models/gemini-2.0-flash-exp",
        OutputModel=OutputModel,
    )

    return output.model_dump()


def get_physical_properties_suggestions(ingredient):
    """Get suggestions for physical properties step"""
    class OutputModel(BaseModel):
        physical_viscosity: str = Field(
            description="Ist das eine Zutaten die gegessen wird? Dann ist es 'solid' oder wenn es eine Zutaten ist die getrunken wird, dann 'beverage'",
            default="solid",
        )
        physical_density: str = Field(
            description="ungefähre physikalische Dichte der Zutat in g/cm³",
            default="1.00",
        )
        durability_in_days: int = Field(
            description="Haltbarkeit der Zutat in Tagen",
            default=None,
        )
        max_storage_temperature: int = Field(
            description="Maximale Lagertemperatur in Grad Celsius",
            default=20,
        )

    output = get_ai_suggestion(
        prompt=f"""
            Gebe mir passende technisch genaue Texte für die Rezepzutat
            ohne Werbung. Sehr sachlich. Kurz. Konkret.
            Entferne alle Mengenangaben und Einheiten. Ohne Markennamen.
            {ingredient.name} {ingredient.description}
        """,
        model="models/gemini-2.0-flash-exp",
        OutputModel=OutputModel,
    )

    return output.model_dump()


def get_nutritional_tags_suggestions(ingredient):
    """Get suggestions for nutritional tags step"""
    class OutputModel(BaseModel):
        nutritional_tags: List[str] = Field(
            description="Liste der Unverträglichkeiten und Allergene, die relevant für diese Zutat sind. Berücksichtige alle wichtigen Nahrungsmittelallergene und Unverträglichkeiten.",
        )

    # Get existing nutritional tag names for reference
    existing_tags = NutritionalTag.objects.all()
    tag_names = [tag.name for tag in existing_tags]

    output = get_ai_suggestion(
        prompt=f"""
            Bestimme potenzielle Unverträglichkeiten und Allergene für diese Zutat: 
            {ingredient.name} {ingredient.description}
            
            Berücksichtige folgende bekannte Allergene/Unverträglichkeiten: {', '.join(tag_names)}
            Antworte nur mit relevanten Allergenen aus dieser Liste.
        """,
        model="models/gemini-2.0-flash-exp",
        OutputModel=OutputModel,
    )

    return output.model_dump()


def get_scores_suggestions(ingredient):
    """Get suggestions for scores step"""
    class OutputModel(BaseModel):
        child_frendly_score: int = Field(
            description="""
            Wie sehr würden sich Kinder darüber freuen diese Zutat zu essen auf einer
            Skala von 1 bis 5. Wobei 1 sehr wenig und 5 sehr viel bedeutet.
            """,
            ge=1,
            le=5,
        )
        scout_frendly_score: int = Field(
            description="""
                Pfadfinderfreundlichkeit der Zutat auf einer Skala von 1 bis 5.
                Wobei 1 sehr wenig und 5 sehr viel bedeutet.
            """,
            ge=1,
            le=5,
        )
        nova_score: int = Field(
            description="""
                NOVA Score der Zutat. Wert von 1 bis 4, wobei 1 unverarbeitete
                Lebensmittel und 4 stark verarbeitete Lebensmittel sind.
            """,
            ge=1,
            le=4,
        )
        environmental_influence_score: int = Field(
            description="""
                Umwelteinfluss der Zutat auf einer Skala von 1 bis 5.
                Wobei 1 sehr umweltfreundlich und 5 sehr umweltschädlich bedeutet.
            """,
            ge=1,
            le=5,
        )

    output = get_ai_suggestion(
        prompt=f"""
            Gebe mir passende technisch genaue Texte für die Rezepzutat
            ohne Werbung. Sehr sachlich. Kurz. Konkret.
            Entferne alle Mengenangaben und Einheiten. Ohne Markennamen.
            {ingredient.name} {ingredient.description}
        """,
        model="models/gemini-2.0-flash-exp",
        OutputModel=OutputModel,
    )

    return output.model_dump()


def get_recipe_info_suggestions(ingredient):
    """Get suggestions for recipe info step"""
    class OutputModel(BaseModel):
        is_unprepaired_consumable: bool = Field(
            description="Gibt an, ob diese Zutat ohne Zubereitung als Snack verzehrt werden kann. True für ja, False für nein.",
            default=False,
        )
        standard_recipe_weight_g: float = Field(
            description="Standardgewicht in Gramm, das in einem Standardrezept verwendet wird. Typischerweise der Wert einer Standardportion.",
            default=100.0,
        )

    output = get_ai_suggestion(
        prompt=f"""
            Gebe mir passende technisch genaue Texte für die Rezepzutat
            ohne Werbung. Sehr sachlich. Kurz. Konkret.
            Entferne alle Mengenangaben und Einheiten. Ohne Markennamen.
            {ingredient.name} {ingredient.description}
        """,
        model="models/gemini-2.0-flash-exp",
        OutputModel=OutputModel,
    )

    return output.model_dump()


def get_nutrition_suggestions(ingredient):
    """Get suggestions for nutrition step"""
    class OutputModel(BaseModel):
        energy_kj: float = Field(
            description="Energiegehalt in kJ pro 100g",
        )
        protein_g: float = Field(
            description="Proteingehalt in g pro 100g",
        )
        fat_g: float = Field(
            description="Fettgehalt in g pro 100g",
        )
        fat_sat_g: float = Field(
            description="Gesättigte Fettsäuren in g pro 100g",
        )
        sodium_mg: float = Field(
            description="Natriumgehalt in mg pro 100g",
        )
        carbohydrate_g: float = Field(
            description="Kohlenhydratgehalt in g pro 100g",
        )
        sugar_g: float = Field(
            description="Zuckergehalt in g pro 100g",
        )
        fibre_g: float = Field(
            description="Ballaststoffgehalt in g pro 100g",
        )
        fruit_factor: float = Field(
            description="Obst, Gemüse, Nüsse, Hülsenfrüchte, Rapsöl, Olivenöl der Zutat für den Nutriscore berechnung. Von 0 bis 100 in %",
        )

    output = get_ai_suggestion(
        prompt=f"""
            Gebe mir passende Nährwerte für die Rezepzutat. Falls nicht bekannt, dann schätze die Werte.
            {ingredient.name} {ingredient.description}
        """,
        model="models/gemini-2.0-flash-exp",
        OutputModel=OutputModel,
    )

    return output.model_dump()
