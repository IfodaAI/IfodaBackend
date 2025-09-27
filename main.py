import math

def get_distance_from_lat_lon_in_km(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the earth in km
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)

    a = (math.sin(dLat / 2) * math.sin(dLat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dLon / 2) * math.sin(dLon / 2))

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = R * c  # Distance in km
    return d

user_location = {"latitude":"","longitude":""}
BRANCHES = [{"latitude":"","longitude":""}]
user_lat = user_location.latitude
user_lon = user_location.longitude
# Calculate distances
for branch in BRANCHES:
    branch_lat = branch['latitude']
    branch_lon = branch['longitude']
    # distance = await constants.get_distance_between_cities(user_lat, user_lon, branch_lat, branch_lon)
    distance = get_distance_from_lat_lon_in_km(user_lat, user_lon, branch_lat, branch_lon)
    branch['distance'] = distance
# Sort branches by distance
sorted(BRANCHES, key=lambda x: x['distance'])[:5]