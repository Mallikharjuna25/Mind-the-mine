"""
Spatial Abstraction Layer
Provides GeoJSON-compatible spatial calculations and data modeling.
Designed so that switching from SQLite (local JSON) to PostgreSQL/PostGIS requires no changes to service callers.
"""

from typing import List, Tuple, Dict, Any, Optional
from pydantic import BaseModel, Field


class GeoPoint(BaseModel):
    latitude: float
    longitude: float
    altitude_m: Optional[float] = None

    def to_geojson(self) -> Dict[str, Any]:
        return {
            "type": "Point",
            "coordinates": [self.longitude, self.latitude] if self.altitude_m is None else [self.longitude, self.latitude, self.altitude_m]
        }

    @classmethod
    def from_geojson(cls, data: Dict[str, Any]) -> "GeoPoint":
        coords = data.get("coordinates", [0.0, 0.0])
        return cls(
            longitude=coords[0],
            latitude=coords[1],
            altitude_m=coords[2] if len(coords) > 2 else None
        )


class GeoPolygon(BaseModel):
    """
    Coordinates format: list of (lat, lng) or GeoJSON rings [[lng, lat], ...]
    """
    points: List[GeoPoint] = Field(default_factory=list)

    def to_geojson(self) -> Dict[str, Any]:
        ring = [[p.longitude, p.latitude] for p in self.points]
        if ring and ring[0] != ring[-1]:
            ring.append(ring[0])  # Close ring for valid GeoJSON
        return {
            "type": "Polygon",
            "coordinates": [ring]
        }

    @classmethod
    def from_geojson(cls, data: Dict[str, Any]) -> "GeoPolygon":
        rings = data.get("coordinates", [[]])
        points = [GeoPoint(longitude=c[0], latitude=c[1]) for c in rings[0]]
        return cls(points=points)

    def contains_point(self, point: GeoPoint) -> bool:
        """
        Ray-casting algorithm to determine if a point is inside this polygon.
        Works directly on coordinates in 2D space.
        """
        if len(self.points) < 3:
            return False

        x = point.longitude
        y = point.latitude
        inside = False

        n = len(self.points)
        p1 = self.points[0]
        for i in range(n + 1):
            p2 = self.points[i % n]
            if y > min(p1.latitude, p2.latitude):
                if y <= max(p1.latitude, p2.latitude):
                    if x <= max(p1.longitude, p2.longitude):
                        if p1.latitude != p2.latitude:
                            x_inters = (y - p1.latitude) * (p2.longitude - p1.longitude) / (p2.latitude - p1.latitude) + p1.longitude
                        if p1.longitude == p2.longitude or x <= x_inters:
                            inside = not inside
            p1 = p2

        return inside


def is_point_in_zone_polygon(lat: float, lng: float, polygon_geojson: Dict[str, Any]) -> bool:
    """Helper function to check if a lat/lng coordinate falls within a GeoJSON polygon"""
    try:
        poly = GeoPolygon.from_geojson(polygon_geojson)
        pt = GeoPoint(latitude=lat, longitude=lng)
        return poly.contains_point(pt)
    except Exception:
        return False
