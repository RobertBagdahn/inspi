
class FoodClassification:
    def get_major_class(self, ndb_number):
        codes = {
            1: "Molkereinprodukte",
            2: "Fleisch und Fisch",
            3: "Eier",
            4: "Nüße und Samen",
            5: "Getreide und Nudeln",
            6: "Obst",
            7: "Gemüse",
            8: "Öle und Fette",
            9: "Süßes und Getränke"
        }
        first_digit = str(ndb_number)[:1]
        return codes[int(first_digit, 10)]

    def get_minor_class(self, ndb_number):
        codes = {
            11: "Milks, milk drinks, yogurts, infant formulas",
            12: "Creams and cream substitutes",
            13: "Milk desserts and sauces",
            14: "Cheeses",
            20: "Meat",
            21: "Beef",
            22: "Pork",
            23: "Lamb, veal, game",
            24: "Poultry",
            25: "Organ meats, frankfurters, sausages, lunchmeats",
            26: "Fish, shellfish",
            27: "Meat, poultry, fish mixtures",
            28: "Frozen meals, soups, gravies ",
            31: "Eggs",
            32: "Egg mixtures",
            33: "Egg substitutes",
            41: "Legumes",
            42: "Nuts, nut butters, nut mixtures",
            43: "Seeds and seed mixtures",
            44: "Carob products",
            50: "Flour and dry mixes",
            51: "Yeast breads, rolls",
            52: "Quick breads",
            53: "Cakes, cookies, pies, pastries, bars",
            54: "Crackers, snack products",
            55: "Pancakes, waffles, French toast, other grain products",
            56: "Pastas, rice, cooked cereals",
            57: "Cereals, not cooked",
            58: "Grain mixtures, frozen meals, soups",
            59: "Meat substitutes",
            61: "Citrus fruits, juices",
            62: "Dried fruits",
            63: "Other fruits",
            64: "Fruit juices and nectars excluding citrus",
            67: "Fruits and juices baby food",
            71: "White potatoes, starchy vegetables",
            72: "Dark-green vegetables",
            73: "Orange vegetables",
            74: "Tomatoes, tomato mixtures",
            75: "Other vegetables",
            76: "Vegetables and mixtures mostly vegetables baby food",
            77: "Vegetables with meat, poultry, fish",
            78: "Mixtures mostly vegetables without meat, poultry, fish",
            81: "Fats",
            82: "Oils",
            83: "Salad dressings",
            89: "‘For use’ with a sandwich or vegetable",
            91: 'Sugars, sweets',
            92: 'Nonalcoholic beverages',
            93: 'Alcoholic beverages',
            94: 'Noncarbonated water',
            95: 'Formulated nutrition beverages, energy drinks, sports drink',
            99: 'Used as an ingredient, not for coding'
        }
        first_digits = str(ndb_number)[:2]
        return codes[int(first_digits, 10)]
