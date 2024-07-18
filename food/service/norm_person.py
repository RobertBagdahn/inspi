class NormPerson:
    def getWeightByAgeAndGender(self, ageInYear: int, gender: str) -> float:
        """
        Returns the weight in kilograms based on the age and gender of the person.

        Parameters:
        ageInYear (int): The age of the person in years.
        gender (str): The gender of the person. Can be either "M" or "F".

        Returns:
        float: The weight of the person in kilograms.
        """
        weightData = {
            "M": {
                "0": 3.5,
                "1": 4.9,
                "2": 6.2,
                "3": 7.4,
                "4": 8.5,
                "5": 9.6,
                "6": 10.5,
                "7": 11.4,
                "8": 12.2,
                "9": 13.0,
                "10": 32.0,
                "11": 38.0,
                "12": 45.0,
                "13": 52.0,
                "14": 60.0,
                "15": 68.0,
                "16": 73.0,
                "17": 77.0,
                "18": 79.0,
                "19": 80.0,
                "20": 80.0,
                "21": 80.0,
                "22": 80.0,
                "23": 80.0,
                "24": 80.0,
                "25": 80.0,
                "26": 80.0,
                "27": 80.0,
                "28": 80.0,
                "29": 80.0,
                "30": 80.0,
                "31": 80.0,
                "32": 80.0,
                "33": 80.0,
                "34": 80.0,
                "35": 80.0,
                "36": 80.0,
                "37": 80.0,
                "38": 80.0,
                "39": 80.0,
                "40": 80.0,
                "41": 80.0,
                "42": 80.0,
                "43": 80.0,
                "44": 80.0,
                "45": 80.0,
                "46": 80.0,
                "47": 80.0,
                "48": 80.0,
                "49": 80.0,
                "50": 80.0,
                "51": 80.0,
                "52": 80.0,
                "53": 80.0,
                "54": 80.0,
                "55": 80.0,
                "56": 80.0,
                "57": 80.0,
                "58": 80.0,
                "59": 80.0,
                "60": 80.0,
                "61": 80.0,
                "62": 80.0,
                "63": 80.0,
                "64": 80.0,
                "65": 80.0,
                "66": 80.0,
                "67": 80.0,
                "68": 80.0,
                "69": 80.0,
                "70": 80.0,
                "71": 80.0,
                "72": 80.0,
                "73": 80.0,
                "74": 80.0,
                "75": 80.0,
                "76": 80.0,
                "77": 80.0,
                "78": 80.0,
                "79": 80.0,
                "80": 80.0,
                "81": 80.0,
                "82": 80.0,
                "83": 80.0,
                "84": 80.0,
                "85": 80.0,
                "86": 80.0,
                "87": 80.0,
                "88": 80.0,
                "89": 80.0,
                "90": 80.0,
                "91": 80.0,
                "92": 80.0,
                "93": 80.0,
                "94": 80.0,
                "95": 80.0,
                "96": 80.0,
                "97": 80.0,
                "98": 80.0,
                "99": 80.0,
            },
            "F": {
                "0": 3.4,
                "1": 4.7,
                "2": 5.8,
                "3": 6.8,
                "4": 7.7,
                "5": 8.5,
                "6": 9.2,
                "7": 9.9,
                "8": 10.5,
                "9": 11.1,
                "10": 31.0,
                "11": 37.0,
                "12": 43.0,
                "13": 49.0,
                "14": 55.0,
                "15": 61.0,
                "16": 64.0,
                "17": 67.0,
                "18": 68.0,
                "19": 69.0,
                "20": 69.0,
                "21": 69.0,
                "22": 69.0,
                "23": 69.0,
                "24": 69.0,
                "25": 69.0,
                "26": 69.0,
                "27": 69.0,
                "28": 69.0,
                "29": 69.0,
                "30": 69.0,
                "31": 69.0,
                "32": 69.0,
                "33": 69.0,
                "34": 69.0,
                "35": 69.0,
                "36": 69.0,
                "37": 69.0,
                "38": 69.0,
                "39": 69.0,
                "40": 69.0,
                "41": 69.0,
                "42": 69.0,
                "43": 69.0,
                "44": 69.0,
                "45": 69.0,
                "46": 69.0,
                "47": 69.0,
                "48": 69.0,
                "49": 69.0,
                "50": 69.0,
                "51": 69.0,
                "52": 69.0,
                "53": 69.0,
                "54": 69.0,
                "55": 69.0,
                "56": 69.0,
                "57": 69.0,
                "58": 69.0,
                "59": 69.0,
                "60": 69.0,
                "61": 69.0,
                "62": 69.0,
                "63": 69.0,
                "64": 69.0,
                "65": 69.0,
                "66": 69.0,
                "67": 69.0,
                "68": 69.0,
                "69": 69.0,
                "70": 69.0,
                "71": 69.0,
                "72": 69.0,
                "73": 69.0,
                "74": 69.0,
                "75": 69.0,
                "76": 69.0,
                "77": 69.0,
                "78": 69.0,
                "79": 69.0,
                "80": 69.0,
                "81": 69.0,
                "82": 69.0,
                "83": 69.0,
                "84": 69.0,
                "85": 69.0,
                "86": 69.0,
                "87": 69.0,
                "88": 69.0,
                "89": 69.0,
                "90": 69.0,
                "91": 69.0,
                "92": 69.0,
                "93": 69.0,
                "94": 69.0,
                "95": 69.0,
                "96": 69.0,
                "97": 69.0,
                "98": 69.0,
                "99": 69.0,
            },
        }
        try:
            if gender in weightData.keys():
                weightInKg = weightData[gender][str(ageInYear)]
            else:
                weightInKg = (
                    weightData["M"][str(ageInYear)]
                    + weightData["F"][str(ageInYear)]
                ) / 2
            return weightInKg
        except:
            return 73.0

    def getHeigthByAgeAndGender(self, ageInYear: int, gender: str) -> int:
        """
        Returns the height in centimeters based on the age and gender provided.

        Parameters:
        ageInYear (int): The age in years of the person.
        gender (str): The gender of the person. Can be either "M" or "F".

        Returns:
        int: The height in centimeters of the person.
        """
        heightData = {
            "M": {
                "0": 49.9,
                "1": 56.6,
                "2": 62.1,
                "3": 67.0,
                "4": 71.2,
                "5": 75.0,
                "6": 78.4,
                "7": 81.4,
                "8": 84.1,
                "9": 86.6,
                "10": 139.0,
                "11": 144.0,
                "12": 149.0,
                "13": 154.0,
                "14": 159.0,
                "15": 165.0,
                "16": 170.0,
                "17": 175.0,
                "18": 179.0,
                "19": 181.0,
                "20": 182.0,
                "21": 182.0,
                "22": 182.0,
                "23": 182.0,
                "24": 182.0,
                "25": 182.0,
                "26": 182.0,
                "27": 182.0,
                "28": 182.0,
                "29": 182.0,
                "30": 181.0,
                "31": 181.0,
                "32": 181.0,
                "33": 181.0,
                "34": 181.0,
                "35": 181.0,
                "36": 181.0,
                "37": 181.0,
                "38": 181.0,
                "39": 181.0,
                "40": 180.0,
                "41": 180.0,
                "42": 180.0,
                "43": 180.0,
                "44": 180.0,
                "45": 180.0,
                "46": 180.0,
                "47": 180.0,
                "48": 180.0,
                "49": 180.0,
                "50": 179.0,
                "51": 179.0,
                "52": 179.0,
                "53": 179.0,
                "54": 179.0,
                "55": 179.0,
                "56": 179.0,
                "57": 179.0,
                "58": 179.0,
                "59": 179.0,
                "60": 178.0,
                "61": 178.0,
                "62": 178.0,
                "63": 178.0,
                "64": 178.0,
                "65": 178.0,
                "66": 178.0,
                "67": 178.0,
                "68": 178.0,
                "69": 178.0,
                "70": 177.0,
                "71": 177.0,
                "72": 177.0,
                "73": 177.0,
                "74": 177.0,
                "75": 177.0,
                "76": 177.0,
                "77": 177.0,
                "78": 177.0,
                "79": 177.0,
                "80": 176.0,
                "81": 176.0,
                "82": 176.0,
                "83": 176.0,
                "84": 176.0,
                "85": 176.0,
                "86": 176.0,
                "87": 176.0,
                "88": 176.0,
                "89": 176.0,
                "90": 175.0,
                "91": 175.0,
                "92": 175.0,
                "93": 175.0,
                "94": 175.0,
                "95": 175.0,
                "96": 175.0,
                "97": 175.0,
                "98": 175.0,
                "99": 175.0,
            },
            "F": {
                "0": 49.0,
                "1": 55.8,
                "2": 61.3,
                "3": 66.2,
                "4": 70.4,
                "5": 74.1,
                "6": 77.4,
                "7": 80.3,
                "8": 82.9,
                "9": 85.3,
                "10": 138.0,
                "11": 143.0,
                "12": 148.0,
                "13": 153.0,
                "14": 158.0,
                "15": 163.0,
                "16": 167.0,
                "17": 170.0,
                "18": 172.0,
                "19": 173.0,
                "20": 173.0,
                "21": 173.0,
                "22": 173.0,
                "23": 173.0,
                "24": 173.0,
                "25": 173.0,
                "26": 173.0,
                "27": 173.0,
                "28": 173.0,
                "29": 173.0,
                "30": 173.0,
                "31": 173.0,
                "32": 173.0,
                "33": 173.0,
                "34": 173.0,
                "35": 173.0,
                "36": 173.0,
                "37": 173.0,
                "38": 173.0,
                "39": 173.0,
                "40": 173.0,
                "41": 173.0,
                "42": 173.0,
                "43": 173.0,
                "44": 173.0,
                "45": 173.0,
                "46": 173.0,
                "47": 173.0,
                "48": 173.0,
                "49": 173.0,
                "50": 173.0,
                "51": 173.0,
                "52": 173.0,
                "53": 173.0,
                "54": 173.0,
                "55": 173.0,
                "56": 173.0,
                "57": 173.0,
                "58": 173.0,
                "59": 173.0,
                "60": 173.0,
                "61": 173.0,
                "62": 173.0,
                "63": 173.0,
                "64": 173.0,
                "65": 173.0,
                "66": 173.0,
                "67": 173.0,
                "68": 173.0,
                "69": 173.0,
                "70": 173.0,
                "71": 173.0,
                "72": 173.0,
                "73": 173.0,
                "74": 173.0,
                "75": 173.0,
                "76": 173.0,
                "77": 173.0,
                "78": 173.0,
                "79": 173.0,
                "80": 173.0,
                "81": 173.0,
                "82": 173.0,
                "83": 173.0,
                "84": 173.0,
                "85": 173.0,
                "86": 173.0,
                "87": 173.0,
                "88": 173.0,
                "89": 173.0,
                "90": 173.0,
                "91": 173.0,
                "92": 173.0,
                "93": 173.0,
                "94": 173.0,
                "95": 173.0,
                "96": 173.0,
                "97": 173.0,
                "98": 173.0,
                "99": 173.0,
            },
        }
        try:
            if gender in heightData.keys():
                heigthInCm = heightData[gender][str(ageInYear)]
            else:
                heigthInCm = (
                    heightData["M"][str(ageInYear)]
                    + heightData["M"][str(ageInYear)]
                ) / 2
            return heigthInCm
        except:
            return 178.0

    def energyByStJeorEquation(
        self,
        ageInYear: int,
        gender: str,
        activityFactor: float,
        heigthInCm: int,
        weightInKg: int,
    ) -> float:
        """
        Calculates the energy expenditure of a person using the St. Jeor equation.

        Args:
            ageInYear (int): Age of the person in years.
            gender (str): Gender of the person. Either "M" or "F".
            activityFactor (float): Activity factor of the person.
            heigthInCm (int): Height of the person in centimeters.
            weightInKg (int): Weight of the person in kilograms.

        Returns:
            float: Energy expenditure of the person in kilojoules.
        """

        energyKj = 0
        energyKj += 10 * weightInKg
        energyKj += 6.25 * heigthInCm
        energyKj += -5 * ageInYear

        if gender == "M":
            energyKj += 5

        if gender == "F":
            energyKj += -161

        energyKj *= activityFactor
        energyKj *= 4.2  # convert kcal to kJ

        return energyKj

    def energyByGenderAndAge(self, gender, ageInYear, activityFactor):
        """
        Returns the energy need of a person based on
        """

        heigthInCm = self.getHeigthByAgeAndGender(ageInYear, gender)
        weightInKg = self.getWeightByAgeAndGender(ageInYear, gender)

        energyKj = self.energyByStJeorEquation(
            ageInYear,
            gender,
            activityFactor,
            heigthInCm,
            weightInKg
        )

        return energyKj

    def get_norm_person(
        self, gender: str = "divers", ageInYear: int = 15, activityFactor: int = 1.5
    ) -> float:
        print(gender, ageInYear, activityFactor)
        print(gender, ageInYear, activityFactor)
        # norm_person
        gender_ref = "M"
        ageInYear_ref = 15
        activityFactor_ref = 1.5
        engery_ref = self.energyByGenderAndAge(
            gender_ref,
            ageInYear_ref,
            activityFactor_ref,
        )

        engery_current = self.energyByGenderAndAge(gender, ageInYear, activityFactor)

        return round(engery_current / engery_ref, 2)
