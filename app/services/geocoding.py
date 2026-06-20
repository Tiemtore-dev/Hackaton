import re
import httpx
import logging

logger = logging.getLogger(__name__)

async def parse_location(url_or_coords: str) -> dict | None:
    """
    Analyser une localisation (coordonnées ou lien Google Maps), extraire les coordonnées
    et faire du reverse-geocoding (Nominatim) pour obtenir la ville, le quartier et l'adresse.
    """
    url_or_coords = url_or_coords.strip()
    lat, lng = None, None
    
    # 1. Vérifier si ce sont des coordonnées brutes (ex: 5.3434, -4.0123)
    coord_match = re.match(r"^\s*(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)\s*$", url_or_coords)
    if coord_match:
        try:
            lat = float(coord_match.group(1))
            lng = float(coord_match.group(2))
        except ValueError:
            pass
    else:
        # C'est un lien. Si c'est un lien raccourci Google Maps, suivre la redirection
        url = url_or_coords
        if "maps.app.goo.gl" in url or "goo.gl/maps" in url:
            try:
                async with httpx.AsyncClient(follow_redirects=True) as client:
                    res = await client.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10.0)
                    url = str(res.url)
            except Exception as e:
                logger.error(f"Error expanding short URL {url_or_coords}: {e}")
        
        # Tenter d'extraire les coordonnées depuis l'URL
        # Pattern 1: @lat,lng
        m1 = re.search(r"@(-?\d+\.\d+),(-?\d+\.\d+)", url)
        if m1:
            try:
                lat = float(m1.group(1))
                lng = float(m1.group(2))
            except ValueError:
                pass
        else:
            # Pattern 2: !3dlat!4dlng
            m2 = re.search(r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)", url)
            if m2:
                try:
                    lat = float(m2.group(1))
                    lng = float(m2.group(2))
                except ValueError:
                    pass
            else:
                # Pattern 3: q=lat,lng
                m3 = re.search(r"[?&]q=(-?\d+\.\d+),(-?\d+\.\d+)", url)
                if m3:
                    try:
                        lat = float(m3.group(1))
                        lng = float(m3.group(2))
                    except ValueError:
                        pass
                        
    if lat is None or lng is None:
        logger.warning(f"Could not extract coordinates from location input: {url_or_coords}")
        return None
        
    # 2. Reverse Geocoding avec Nominatim (OpenStreetMap)
    geocoding_url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=json&accept-language=fr"
    headers = {"User-Agent": "SportMeetApp/1.0 (contact@sportmeet.com)"}
    
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(geocoding_url, headers=headers, timeout=10.0)
            if res.status_code == 200:
                data = res.json()
                addr = data.get("address", {})
                
                # Extraire ville, quartier, route
                city = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("county") or "Abidjan"
                neighborhood = addr.get("neighbourhood") or addr.get("suburb") or addr.get("quarter") or addr.get("city_district") or "Cocody"
                road = addr.get("road") or addr.get("amenity") or addr.get("building") or addr.get("suburb") or ""
                
                # Nom du lieu
                name = data.get("display_name", "").split(",")[0]
                if name.replace(".", "").replace("-", "").isdigit():
                    name = ""
                    
                return {
                    "name": name or road or f"Terrain à {neighborhood}",
                    "address": road or data.get("display_name", ""),
                    "city": city,
                    "neighborhood": neighborhood,
                    "latitude": lat,
                    "longitude": lng,
                    "google_maps_url": url_or_coords if "http" in url_or_coords else None
                }
    except Exception as e:
        logger.error(f"Geocoding request failed for lat={lat}, lon={lng}: {e}")
        
    return {
        "name": f"Terrain à {lat}, {lng}",
        "address": f"Coordonnées: {lat}, {lng}",
        "city": "Abidjan",
        "neighborhood": "Cocody",
        "latitude": lat,
        "longitude": lng,
        "google_maps_url": url_or_coords if "http" in url_or_coords else None
    }
