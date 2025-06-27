def get_persona_score(data):
    # Accessing values from JSON file
    user_id = data['user_id']
    username = data['username']
    score = int(data['predicted_score'])  # convert from string to int if needed

    carbon_footprint = data['factory_impact']['carbon_footprint']
    water_usage = data['factory_impact']['water_usage']

    washing_impact_kWh = float(data['washing_machine_impact'][0])
    washing_impact_litres = float(data['washing_machine_impact'][1])

    disposal = data['disposal']


    # Max and Min values based on actual user data
    min_carbon, max_carbon = 2.252, 8.4768
    min_water, max_water = 487.77, 2451.15
    min_kWh, max_kWh = 39.0, 1086.8
    min_litres, max_litres = 3148.08, 34628.88


    # Map function
    def map_range(value, in_min, in_max, out_min, out_max):
        return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    # Mapping data
    carbon_mapped = round(map_range(carbon_footprint, min_carbon, max_carbon, 1, 100), 2)
    water_mapped = round(map_range(water_usage, min_water, max_water, 1, 100), 2)
    washing_kWh_mapped = round(map_range(washing_impact_kWh, min_kWh, max_kWh, 1, 100), 2)
    washing_litres_mapped = round(map_range(washing_impact_litres, min_litres, max_litres, 1, 100), 2)
    disposal_mapped = {
        "Donation": 15,
        "Recycle": 40,
        "Landfill": 85
    }.get(disposal, 0)  # 0 as default if not found


    def give_persona():
        score = round((carbon_mapped + water_mapped + washing_kWh_mapped + washing_litres_mapped + disposal_mapped) / 5, 2)
        score = 100 - score
        if 0 <= score <= 20: return 1
        elif 20 < score <= 40: return 2
        elif 40 < score <= 60: return 3
        elif 60 < score <= 80: return 4
        elif 80 < score <= 100: return 5
        return 0

    def return_persona_score():
        return round((carbon_mapped + water_mapped + washing_kWh_mapped + washing_litres_mapped + disposal_mapped) / 5, 2)

    return give_persona(), return_persona_score()