"""
Geospatial utility functions for WORK4FOOD
Handles distance calculations and location generation on Earth's surface
"""
from typing import Tuple, List, Optional
import math
import random
import numpy as np


def haversine_km(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """
    Calculate the great circle distance between two points on Earth using the Haversine formula.
    Args:
        coord1: (latitude, longitude) in decimal degrees
        coord2: (latitude, longitude) in decimal degrees
    Returns:
        Distance in kilometers
    """
    lat1, lon1 = np.radians(coord1[0]), np.radians(coord1[1])
    lat2, lon2 = np.radians(coord2[0]), np.radians(coord2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2)
    c = 2 * np.arcsin(np.sqrt(a))
    R = 6371.0
    return float(R * c)


def travel_time_minutes(coord1: Tuple[float, float], coord2: Tuple[float, float], speed_kmph: float = 25.0) -> float:
    """
    Calculate travel time between two points given a speed.
    Returns travel time in minutes.
    """
    distance_km = haversine_km(coord1, coord2)
    time_hours = distance_km / max(speed_kmph, 0.001)
    return float(time_hours * 60.0)


def random_point(center: Tuple[float, float], radius_km: float) -> Tuple[float, float]:
    """
    Generate a random point within a circular radius of a center point.
    Uses uniform distribution in circular area.
    """
    bearing = random.random() * 2 * math.pi
    r = radius_km * math.sqrt(random.random())
    dx = r * math.cos(bearing)
    dy = r * math.sin(bearing)
    center_lat, center_lon = center
    lat_offset = dy / 111.0
    lon_offset = dx / (111.0 * math.cos(math.radians(center_lat)))
    return (center_lat + lat_offset, center_lon + lon_offset)


def random_point_clustered(center: Tuple[float, float], radius_km: float, cluster_factor: float = 0.3) -> Tuple[float, float]:
    """
    Generate a random point with clustering tendency (for restaurant hotspots).
    """
    hotspot_radius = radius_km * cluster_factor
    hotspot = random_point(center, hotspot_radius)
    point_radius = radius_km * (1 - cluster_factor)
    return random_point(hotspot, point_radius)


def calculate_bounding_box(center: Tuple[float, float], radius_km: float) -> Tuple[float, float, float, float]:
    """
    Calculate bounding box (min/max lat/lon) for a circular area.
    Returns (min_lat, max_lat, min_lon, max_lon)
    """
    lat, lon = center
    lat_offset = radius_km / 111.0
    lon_offset = radius_km / (111.0 * math.cos(math.radians(lat)))
    return (lat - lat_offset, lat + lat_offset, lon - lon_offset, lon + lon_offset)


def is_within_radius(point: Tuple[float, float], center: Tuple[float, float], radius_km: float) -> bool:
    """Check if a point is within a circular radius of a center."""
    return haversine_km(point, center) <= radius_km


def find_nearest(target: Tuple[float, float], candidates: List[Tuple[float, float]]) -> Tuple[Optional[int], float]:
    """
    Find the nearest location from a list of candidates.
    Returns (index, distance_km). If no candidates, returns (None, inf).
    """
    if not candidates:
        return None, float("inf")
    min_distance = float("inf")
    nearest_idx = 0
    for i, candidate in enumerate(candidates):
        dist = haversine_km(target, candidate)
        if dist < min_distance:
            min_distance = dist
            nearest_idx = i
    return nearest_idx, float(min_distance)


def bearing_between(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """Calculate the initial bearing (direction) from coord1 to coord2 in degrees."""
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    dlon = lon2 - lon1
    x = math.sin(dlon) * math.cos(lat2)
    y = (math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon))
    bearing_rad = math.atan2(x, y)
    bearing_deg = math.degrees(bearing_rad)
    return (bearing_deg + 360) % 360


def destination_point(start: Tuple[float, float], bearing_deg: float, distance_km: float) -> Tuple[float, float]:
    """Calculate destination point given start, bearing, and distance."""
    R = 6371.0
    lat1 = math.radians(start[0])
    lon1 = math.radians(start[1])
    bearing = math.radians(bearing_deg)
    lat2 = math.asin(
        math.sin(lat1) * math.cos(distance_km / R) + math.cos(lat1) * math.sin(distance_km / R) * math.cos(bearing)
    )
    lon2 = lon1 + math.atan2(
        math.sin(bearing) * math.sin(distance_km / R) * math.cos(lat1),
        math.cos(distance_km / R) - math.sin(lat1) * math.sin(lat2),
    )
    return (math.degrees(lat2), math.degrees(lon2))


CITY_CENTERS = {
    "mumbai": (19.0760, 72.8777),
    "delhi": (28.6139, 77.2090),
    "bangalore": (12.9716, 77.5946),
    "hyderabad": (17.3850, 78.4867),
    "chennai": (13.0827, 80.2707),
    "kolkata": (22.5726, 88.3639),
    "pune": (18.5204, 73.8567),
    "ahmedabad": (23.0225, 72.5714),
}


def get_city_center(city_name: str) -> Tuple[float, float]:
    """Get predefined city center; defaults to Mumbai."""
    return CITY_CENTERS.get(city_name.lower(), CITY_CENTERS["mumbai"])

