def get_restaurants(city=None, locality=None, hotel_name=None):
    
    restaurants = [
        {"city": "Mumbai", "locality": "West Mumbai", "hotel_name": "Taj Hotel", "cuisine": "Indian", "rating": 4.5},
        {"city": "Mumbai", "locality": "West Mumbai", "hotel_name": "Rivin Mahal", "cuisine": "Indian", "rating": 4.5},
        {"city": "Mumbai", "locality": "West Mumbai", "hotel_name": "Hotel by Marriott", "cuisine": "Indian", "rating": 4.5},
        {"city": "Mumbai", "locality": "West Mumbai", "hotel_name": "Sea View Resort", "cuisine": "Seafood", "rating": 4.2},
        {"city": "Mumbai", "locality": "East Mumbai", "hotel_name": "City Palace", "cuisine": "Chinese", "rating": 4.1},
        {"city": "Delhi", "locality": "South Delhi", "hotel_name": "Royal Palace", "cuisine": "Mughlai", "rating": 4.6},
        {"city": "Bangalore", "locality": "Indiranagar", "hotel_name": "Green Stay", "cuisine": "Continental", "rating": 4.3},
        {"city": "Chennai", "locality": "T Nagar", "hotel_name": "Grand Inn", "cuisine": "South Indian", "rating": 4.4},
    ]

    results = []

    for r in restaurants:
        match = False

        if city and city.lower() in r["city"].lower():
            match = True
        if locality and locality.lower() in r["locality"].lower():
            match = True
        if hotel_name and hotel_name.lower() in r["hotel_name"].lower():
            match = True

        if not any([city, locality, hotel_name]):
            match = True

        if match:
            results.append(r)

    if len(results) < 3:
        for r in restaurants:
            if r not in results:
                results.append(r)
            if len(results) >= 3:
                break

    return results
