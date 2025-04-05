def get_nutri_table():
    return {
        "energy_kj": {
            "solid": [
                [-10000, 335, 0],
                [335, 670, 1],
                [670, 1005, 2],
                [1005, 1340, 3],
                [1340, 1675, 4],
                [1675, 2010, 5],
                [2010, 2345, 6],
                [2345, 2680, 7],
                [2680, 3015, 8],
                [3015, 3350, 9],
                [3350, 10000, 10],
            ],
            "beverage": [
                [-10000, 0, 0],
                [0, 30, 1],
                [30, 60, 2],
                [60, 90, 3],
                [90, 120, 4],
                [120, 150, 5],
                [150, 180, 6],
                [180, 210, 7],
                [210, 240, 8],
                [240, 270, 9],
                [270, 10000, 10],
            ],
        },
        "sugar_g": {
            "solid": [
                [-10000, 4.5, 0],
                [4.5, 9, 1],
                [9, 13.5, 2],
                [13.5, 18, 3],
                [18, 22.5, 4],
                [22.5, 27, 5],
                [27, 31, 6],
                [31, 36, 7],
                [36, 40, 8],
                [40, 45, 9],
                [45, 10000, 10],
            ],
            "beverage": [
                [-10000, 0, 0],
                [0, 1.5, 1],
                [1.5, 3, 2],
                [3, 4.5, 3],
                [4.5, 6, 4],
                [6, 7.5, 5],
                [7.5, 9, 6],
                [9, 10.5, 7],
                [10.5, 12, 8],
                [12, 13.5, 9],
                [13.5, 10000, 10],
            ],
        },
        "fibre_g": {
            "solid": [
                [-10000, 0.9, 0],
                [0.9, 1.9, -1],
                [1.9, 2.8, -2],
                [2.8, 3.7, -3],
                [3.7, 4.7, -4],
                [4.7, 10000, -5],
            ],
            "beverage": [
                [-10000, 0.9, 0],
                [0.9, 1.9, -1],
                [1.9, 2.8, -2],
                [2.8, 3.7, -3],
                [3.7, 4.7, -4],
                [4.7, 10000, -5],
            ],
        },
        "protein_g": {
            "solid": [
                [-10000, 1.6, 0],
                [1.6, 3.2, -1],
                [3.2, 4.8, -2],
                [4.8, 6.4, -3],
                [6.4, 8, -4],
                [8, 10000, -5],
            ],
            "beverage": [
                [-10000, 1.6, 0],
                [1.6, 3.2, -1],
                [3.2, 4.8, -2],
                [4.8, 6.4, -3],
                [6.4, 8, -4],
                [8, 10000, -5],
            ],
        },
        "sodium_mg": {
            "solid": [
                [-10000, 90, 0],
                [90, 180, 1],
                [180, 270, 2],
                [270, 360, 3],
                [360, 450, 4],
                [450, 540, 5],
                [540, 630, 6],
                [630, 720, 7],
                [720, 810, 8],
                [810, 900, 9],
                [900, 10000, 10],
            ],
            "beverage": [
                [-10000, 90, 0],
                [90, 180, 1],
                [180, 270, 2],
                [270, 360, 3],
                [360, 450, 4],
                [450, 540, 5],
                [540, 630, 6],
                [630, 720, 7],
                [720, 810, 8],
                [810, 900, 9],
                [900, 10000, 10],
            ],
        },
        "fruit_factor": {
            "solid": [
                [-10000, 40, 0],
                [0.40, 60, -1],
                [0.60, 80, -2],
                [0.80, 10000, -5],
            ],
            "beverage": [
                [-10000, 40, 0],
                [0.40, 60, -2],
                [0.60, 80, -4],
                [0.80, 10000, -10],
            ],
        },
        "fat_sat_g": {
            "solid": [
                [-10000, 1, 0],
                [1, 2, 1],
                [2, 3, 2],
                [3, 4, 3],
                [4, 5, 4],
                [5, 6, 5],
                [6, 7, 6],
                [7, 8, 7],
                [8, 9, 8],
                [9, 10, 9],
                [10, 10000, 10],
            ],
            "beverage": [
                [-10000, 1, 0],
                [1, 2, 1],
                [2, 3, 2],
                [3, 4, 3],
                [4, 5, 4],
                [5, 6, 5],
                [6, 7, 6],
                [7, 8, 7],
                [8, 9, 8],
                [9, 10, 9],
                [10, 10000, 10],
            ],
        },
        "nutriClass": {
            "solid": [
                [-10000, -1, 1],
                [-1, 3, 2],
                [3, 11, 3],
                [11, 19, 4],
                [19, 10000, 5],
            ],
            "beverage": [[-10000, 1, 2], [2, 5, 3], [5, 9, 4], [9, 10000, 5]],
        },
    }


def get_nutri_items():
    return [
        "energy_kj",
        "sugar_g",
        "fibre_g",
        "protein_g",
        "sodium_mg",
        "fruit_factor",
        "fat_sat_g",
    ]


def get_points(item, physical_viscosity, value):
    if not value:
        return 0
    get_nutri_table_data = get_nutri_table()
    nutri_array = get_nutri_table_data[item][physical_viscosity]
    for row in nutri_array:
        if (row[0] <= value) and (row[1] >= value):
            return row[2]
    return 0


def get_nutri_class(physical_viscosity, value):
    if value is None:
        return 0
    get_nutri_table_data = get_nutri_table()
    nutri_array = get_nutri_table_data["nutriClass"][physical_viscosity]
    for row in nutri_array:
        if (row[0] <= value) and (row[1] >= value):
            return row[2]
    return 0


def update_meta_info_nutri(recipe, recipe_items):
    """
    Update a recipe.
    """

    fields = get_nutri_items()

    for item in recipe_items:
        meta_info = item.meta_info

        # Only process if item.portion exists
        if hasattr(item, 'portion') and item.portion:
            ingredient_meta_info = item.portion.ingredient.meta_info

            for field in fields:
                points = getattr(ingredient_meta_info, f"nutri_points_{field}", 0)
                setattr(meta_info, f"nutri_points_{field}", points)
                
                setattr(
                    meta_info,
                    "nutri_points",
                    sum(getattr(meta_info, f"nutri_points_{field}") for field in fields),
                )
                setattr(
                    meta_info,
                    "nutri_class",
                    get_nutri_class("solid", meta_info.nutri_points),
                )
        meta_info.save()

    recipe_meta_info = recipe.meta_info
    # Calculate weighted nutri points for the recipe
    total_weight = sum(item.meta_info.weight_g for item in recipe_items if hasattr(item.meta_info, 'weight_g') and item.meta_info.weight_g)


    if total_weight > 0:
        # Initialize all fields to 0
        for field in fields:
            setattr(recipe_meta_info, f"nutri_points_{field}", 0)
        
        # Calculate weighted sum for each nutrient
        for item in recipe_items:
            if hasattr(item.meta_info, 'weight_g') and item.meta_info.weight_g:
                weight_factor = item.meta_info.weight_g / total_weight
                for field in fields:
                    item_points = getattr(item.meta_info, f"nutri_points_{field}", 0) or 0
                    current_points = getattr(recipe_meta_info, f"nutri_points_{field}", 0) or 0
                    weighted_points = item_points * weight_factor
                    setattr(recipe_meta_info, f"nutri_points_{field}", current_points + weighted_points)
        
        # Calculate total nutri points and class
        recipe_meta_info.nutri_points = sum(getattr(recipe_meta_info, f"nutri_points_{field}", 0) or 0 for field in fields)
        recipe_meta_info.nutri_class = get_nutri_class("solid", recipe_meta_info.nutri_points)
        recipe_meta_info.save()

def update_meta_info_nutri_portions(ingredient):
    """
    Update all portions connected to the ingredient.
    """
    fields = get_nutri_items()
    
    for portion in ingredient.portions.all():
        meta_info = portion.meta_info

        # Copy nutri score and nutri points from ingredient
        for field in fields:
            value = getattr(ingredient.meta_info, field)
            points = get_points(field, "solid", value)
            setattr(meta_info, f"nutri_points_{field}", points)
        # set nutri points
        setattr(
            meta_info,
            "nutri_points",
            sum(getattr(meta_info, f"nutri_points_{field}") for field in fields),
        )
        setattr(
            meta_info,
            "nutri_class",
            get_nutri_class("solid", meta_info.nutri_points),
        )
        meta_info.save()

def update_portions_with_ingredient_data(ingredient):
    """
    Update all portions nutrients based on ingredient data (per 100g) and portion weight.
    """
    meta_info_ingredient = ingredient.meta_info
    fields = get_nutri_items()
    
    for portion in ingredient.portions.all():
        meta_info_portion = portion.meta_info
        weight_factor = meta_info_portion.weight_g / 100.0  # Calculate factor (portion weight / 100g)
        
        for field in fields:
            # Skip if field doesn't exist on the model
            if not hasattr(meta_info_ingredient, field):
                continue
                
            # Get value from ingredient (per 100g) and multiply by weight factor
            ingredient_value = getattr(meta_info_ingredient, field, 0)
            if ingredient_value is not None:
                portion_value = ingredient_value * weight_factor
                setattr(meta_info_portion, field, portion_value)
        
        meta_info_portion.save()



def update_meta_info_nutri_ingredient(ingredient):
    """
    Update a recipe.
    """

    fields = get_nutri_items()

    meta_info = ingredient.meta_info
    for field in fields:
        value = getattr(meta_info, field)
        points = get_points(field, "solid", value)
        setattr(meta_info, f"nutri_points_{field}", points)

    # set nutri points
    setattr(
        meta_info,
        "nutri_points",
        sum(getattr(meta_info, f"nutri_points_{field}") for field in fields),
    )

    setattr(
        meta_info,
        "nutri_class",
        get_nutri_class("solid", meta_info.nutri_points),
    )
    meta_info.save()

    update_portions_with_ingredient_data(ingredient)
    update_meta_info_nutri_portions(ingredient)
