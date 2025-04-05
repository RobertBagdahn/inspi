from activity.activity.service.admin.ai_suggestion import get_ai_suggestion
from pydantic import Field, BaseModel
from typing import List, Optional
from ..models import NutritionalTag, RetailSection

def get_basic_info_suggestions(ingredient_name):
    """Get AI suggestions for the basic_info step."""
    from ..models import RetailSection
    
    retail_sections = RetailSection.objects.all()
    retail_sections_list = [section.name for section in retail_sections]
    
    class BasicInfoModel(BaseModel):
        name: str = Field(
            min_length=5,
            max_length=100,
            description="Name der Zutat. Kurz und prägnant. Ohne Mengenangaben. Ohne Sonderzeichen. Ohne Werbung. Ohne Markennamen.",
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
            {ingredient_name}
        """,
        model="models/gemini-2.0-flash-exp",
        OutputModel=BasicInfoModel,
    )

    result = output.model_dump()
    retail_section_index = None
    if hasattr(output, 'retail_section') and output.retail_section:
        try:
            retail_section_index = retail_sections_list.index(output.retail_section) + 1
        except ValueError:
            # If the section name isn't in our list, leave it as None
            pass

    # Convert output to dictionary and update the retail_section value
    result['retail_section'] = retail_section_index

    return_obj = output.model_dump()
    
    return result

def get_physical_properties_suggestions(ingredient_name):
    """Get AI suggestions for the physical_properties step."""
    class PhysicalPropertiesModel(BaseModel):
        physical_viscosity: str = Field(
            description="Ist das eine Zutaten die gegessen wird? Dann ist es 'solid' oder wenn es eine Zutaten ist die getrunken wird, dann 'beverage'",
            default="solid",
        )
        physical_density: float = Field(
            description="ungefähre physikalische Dichte der Zutat in g/cm³",
            default=1.00,
        )
        durability_in_days: int = Field(
            description="Haltbarkeit der Zutat in Tagen",
            default=30,
        )
        max_storage_temperature: int = Field(
            description="Maximale Lagertemperatur in Grad Celsius",
            default=20,
        )
    
    output = get_ai_suggestion(
        prompt=f"""
            Gebe mir passende physikalische Eigenschaften für die Zutat: {ingredient_name}
            Sei präzise und technisch korrekt. Berücksichtige Standardbedingungen für Lagerung und Haltbarkeit.
        """,
        model="models/gemini-2.0-flash-exp",
        OutputModel=PhysicalPropertiesModel,
    )
    
    return output.model_dump()

def get_nutritional_tags_suggestions(ingredient_name):
    """Get AI suggestions for the nutritional_tags step."""
    nutritional_tags = NutritionalTag.objects.all()
    tag_names = [tag.name for tag in nutritional_tags]
    
    class NutritionalTagsModel(BaseModel):
        nutritional_tags: List[str] = Field(
            description="Liste der Unverträglichkeiten und Allergene, die relevant für diese Zutat sind.",
            default=[],
        )
    
    output = get_ai_suggestion(
        prompt=f"""
            Bestimme potenzielle Unverträglichkeiten und Allergene für diese Zutat: {ingredient_name}
            
            Berücksichtige folgende bekannte Allergene/Unverträglichkeiten: {', '.join(tag_names)}
            Antworte nur mit relevanten Allergenen aus dieser Liste.
        """,
        model="models/gemini-2.0-flash-exp",
        OutputModel=NutritionalTagsModel,
    )
    
    # Get the tag objects for the suggested tag names
    tag_objects = []
    for tag_name in output.nutritional_tags:
        try:
            tag = NutritionalTag.objects.get(name=tag_name)
            tag_objects.append(tag.id)
        except NutritionalTag.DoesNotExist:
            pass
    
    result = output.model_dump()
    result['nutritional_tags'] = tag_objects
    return result

def get_scores_suggestions(ingredient_name):
    """Get AI suggestions for the scores step."""
    class ScoresModel(BaseModel):
        child_frendly_score: int = Field(
            description="Wie sehr würden sich Kinder darüber freuen diese Zutat zu essen auf einer Skala von 1 bis 5. Wobei 1 sehr wenig und 5 sehr viel bedeutet.",
            ge=1,
            le=5,
        )
        scout_frendly_score: int = Field(
            description="Pfadfinderfreundlichkeit der Zutat auf einer Skala von 1 bis 5. Wobei 1 sehr wenig und 5 sehr viel bedeutet.",
            ge=1,
            le=5,
        )
        nova_score: int = Field(
            description="NOVA Score der Zutat. Wert von 1 bis 4, wobei 1 unverarbeitete Lebensmittel und 4 stark verarbeitete Lebensmittel sind.",
            ge=1,
            le=4,
        )
        environmental_influence_score: int = Field(
            description="Umwelteinfluss der Zutat auf einer Skala von 1 bis 5. Wobei 1 sehr umweltfreundlich und 5 sehr umweltschädlich bedeutet.",
            ge=1,
            le=5,
        )
    
    output = get_ai_suggestion(
        prompt=f"""
            Bewerte die Zutat {ingredient_name} nach folgenden Kriterien:
            1. Kinderfreundlichkeit (1-5)
            2. Pfadfinderfreundlichkeit (1-5)
            3. NOVA-Score für Verarbeitungsgrad (1-4)
            4. Umwelteinfluss (1-5)
        """,
        model="models/gemini-2.0-flash-exp",
        OutputModel=ScoresModel,
    )
    
    return output.model_dump()

def get_recipe_info_suggestions(ingredient_name):
    """Get AI suggestions for the recipe_info step."""
    class RecipeInfoModel(BaseModel):
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
            Für die Zutat {ingredient_name}, bestimme:
            1. Ob sie ohne Zubereitung direkt verzehrt werden kann
            2. Das typische Gewicht in Gramm, das in einem Standardrezept verwendet wird
        """,
        model="models/gemini-2.0-flash-exp",
        OutputModel=RecipeInfoModel,
    )
    
    return output.model_dump()

def get_nutrition_suggestions(ingredient_name):
    """Get AI suggestions for the nutrition step."""
    class NutritionModel(BaseModel):
        energy_kj: float = Field(
            description="Energiegehalt in kJ pro 100g",
            default=0.0,
        )
        protein_g: float = Field(
            description="Proteingehalt in g pro 100g",
            default=0.0,
        )
        fat_g: float = Field(
            description="Fettgehalt in g pro 100g",
            default=0.0,
        )
        fat_sat_g: float = Field(
            description="Gesättigte Fettsäuren in g pro 100g",
            default=0.0,
        )
        sodium_mg: float = Field(
            description="Natriumgehalt in mg pro 100g",
            default=0.0,
        )
        carbohydrate_g: float = Field(
            description="Kohlenhydratgehalt in g pro 100g",
            default=0.0,
        )
        sugar_g: float = Field(
            description="Zuckergehalt in g pro 100g",
            default=0.0,
        )
        fibre_g: float = Field(
            description="Ballaststoffgehalt in g pro 100g",
            default=0.0,
        )
        fruit_factor: float = Field(
            description="Obst, Gemüse, Nüsse, Hülsenfrüchte, Rapsöl, Olivenöl der Zutat für den Nutriscore berechnung. Von 0 bis 100 in %",
            default=0.0,
        )
    
    output = get_ai_suggestion(
        prompt=f"""
            Gebe mir passende Nährwerte für 100g der Zutat: {ingredient_name}
            Sei präzise und technisch korrekt.
        """,
        model="models/gemini-2.0-flash-exp",
        OutputModel=NutritionModel,
    )
    
    return output.model_dump()

def get_suggestions_for_step(step_name, ingredient_name):
    """Get suggestions for a specific wizard step."""
    suggestion_functions = {
        'basic_info': get_basic_info_suggestions,
        'physical_properties': get_physical_properties_suggestions,
        'nutritional_tags': get_nutritional_tags_suggestions,
        'scores': get_scores_suggestions,
        'recipe_info': get_recipe_info_suggestions,
        'nutrition': get_nutrition_suggestions,
    }
    
    if step_name in suggestion_functions:
        return suggestion_functions[step_name](ingredient_name)
    
    return {}
