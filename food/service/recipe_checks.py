def get_hungriness_obj(recipe):
    """
    Get hungriness object for a recipe.

    Args:
        recipe: Recipe object to evaluate

    Returns:
        Dictionary with hungriness information
    """
    # Default values
    hungriness = {"score": 0, "description": "", "level": "medium"}

    # Calculate hungriness score based on recipe properties
    # This is a placeholder - implement actual calculation logic
    if hasattr(recipe, "calories") and recipe.calories:
        if recipe.calories > 600:
            hungriness["score"] = 5
            hungriness["description"] = "Very filling meal"
            hungriness["level"] = "high"
        elif recipe.calories > 350:
            hungriness["score"] = 3
            hungriness["description"] = "Satisfying meal"
            hungriness["level"] = "medium"
        else:
            hungriness["score"] = 1
            hungriness["description"] = "Light meal or snack"
            hungriness["level"] = "low"

    return hungriness


def get_price_obj(recipe):
    """
    Get price object for a recipe.

    Args:
        recipe: Recipe object to evaluate

    Returns:
        Dictionary with price information
    """
    # Default values
    price = {"score": 0, "description": "", "level": "medium"}

    # Calculate price score based on recipe properties
    # This is a placeholder - implement actual calculation logic
    if hasattr(recipe, "estimated_cost") and recipe.estimated_cost:
        if recipe.estimated_cost > 15:
            price["score"] = 1
            price["description"] = "Expensive ingredients"
            price["level"] = "high"
        elif recipe.estimated_cost > 8:
            price["score"] = 3
            price["description"] = "Moderately priced"
            price["level"] = "medium"
        else:
            price["score"] = 5
            price["description"] = "Budget-friendly"
            price["level"] = "low"

    return price


def get_health_obj(recipe, recipe_items):
    """
    Get health object for a recipe.

    Args:
        recipe: Recipe object to evaluate

    Returns:
        Dictionary with health information
    """
    # Default values
    health = {
        "score": 0,
        "description": "",
        "level": "medium",
        "nutri_points": 0,
        "ingredients_unhealthy_rank": [],
    }

    # Handle case when nutri_points is None
    if (
        not hasattr(recipe, "meta_info")
        or not hasattr(recipe.meta_info, "nutri_points")
        or recipe.meta_info.nutri_points is None
    ):
        health["score"] = 3
        health["description"] = "Nährwertinformationen nicht verfügbar"
        health["level"] = "medium"
        health["nutri_points"] = 0
    elif recipe.meta_info.nutri_points < 0:
        health["score"] = 5
        health["description"] = "Sehr gesunde Wahl"
        health["level"] = "high"
    elif recipe.meta_info.nutri_points < 3:
        health["score"] = 4
        health["description"] = "Gesunde Wahl"
        health["level"] = "medium-high"
    elif recipe.meta_info.nutri_points < 5:
        health["score"] = 3
        health["description"] = "Durchschnittlicher Nährwert"
        health["level"] = "medium"
    elif recipe.meta_info.nutri_points < 10:
        health["score"] = 2
        health["description"] = "Weniger gesunde Option"
        health["level"] = "medium-low"
    elif recipe.meta_info.nutri_points < 21:
        health["score"] = 1
        health["description"] = "Nicht für regelmäßigen Verzehr empfohlen"
        health["level"] = "low"

    health["nutri_points"] = recipe.meta_info.nutri_points

    # Add unhealthy ingredients to the health object
    unhealthy_ingredients = []
    for item in recipe_items:
        if (
            hasattr(item, "meta_info")
            and hasattr(item.meta_info, "nutri_points")
            and item.meta_info.nutri_points is not None
        ):
            if (
                hasattr(item.meta_info, "weight_g")
                and item.meta_info.weight_g is not None
            ):
                unhealthy_rank = item.meta_info.nutri_points * item.meta_info.weight_g
            else:
                unhealthy_rank = item.meta_info.nutri_points

            if unhealthy_rank > 0:
                unhealthy_ingredients.append(
                    {
                        "name": (
                            item.portion.ingredient.name
                            if hasattr(item, "portion")
                            and hasattr(item.portion, "ingredient")
                            else "Unknown"
                        ),
                        "nutri_points": item.meta_info.nutri_points,
                        "weight_g": getattr(item.meta_info, "weight_g", 0),
                        "unhealthy_rank": unhealthy_rank,
                    }
                )

    # Sort ingredients by unhealthy rank in descending order
    unhealthy_ingredients.sort(key=lambda x: x["unhealthy_rank"], reverse=True)

    # Add to health object
    health["ingredients_unhealthy_rank"] = unhealthy_ingredients

    return health


def get_taste_obj(recipe):
    """
    Get taste object for a recipe.

    Args:
        recipe: Recipe object to evaluate

    Returns:
        Dictionary with taste information
    """
    # Default values
    taste = {"score": 0, "description": "", "level": "medium"}

    # Calculate taste score based on recipe properties
    # This is a placeholder - implement actual calculation logic
    if hasattr(recipe, "flavor_profile") and recipe.flavor_profile:
        # Example: flavor_profile could be a value from 1-10
        if recipe.flavor_profile > 8:
            taste["score"] = 5
            taste["description"] = "Delicious and flavorful"
            taste["level"] = "high"
        elif recipe.flavor_profile > 5:
            taste["score"] = 3
            taste["description"] = "Good taste"
            taste["level"] = "medium"
        else:
            taste["score"] = 1
            taste["description"] = "Simple flavors"
            taste["level"] = "low"

    return taste
