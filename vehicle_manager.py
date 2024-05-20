import requests, math
from requests.exceptions import HTTPError


class Vehicle:
    def __init__(
        self,
        name: str,
        model: str,
        year: int,
        color: str,
        price: int,
        latitude: float,
        longitude: float,
        id: int | None = None,
    ):
        self.id = id
        self.name = name
        self.model = model
        self.year = year
        self.color = color
        self.price = price
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return (
            f"<Vehicle: {self.name} {self.model} {self.year} {self.color} {self.price}>"
        )

    def to_dict(self):
        vehicle_dict = {
            "name": self.name,
            "model": self.model,
            "year": self.year,
            "color": self.color,
            "price": self.price,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }

        if self.id is not None:
            vehicle_dict["id"] = self.id

        return vehicle_dict


class VehicleManager:
    def __init__(self, url):
        self.url = url

    def get_vehicles(self):
        try:

            response = requests.get(f"{self.url}/vehicles")
            response.raise_for_status()
            vehicles_data = response.json()
            return [Vehicle(**data) for data in vehicles_data]

        except HTTPError as e:
            print(f"Error: {e}")

    def filter_vehicles(self, params: dict):
        vehicles = self.get_vehicles()
        filtered_vehicles = []

        for vehicle in vehicles:
            match = True
            for key, value in params.items():
                if getattr(vehicle, key) != value:
                    match = False
                    break
            if match:
                filtered_vehicles.append(vehicle)

        return filtered_vehicles

    def get_vehicle(self, vehicle_id: int):
        try:

            response = requests.get(f"{self.url}/vehicles/{vehicle_id}")
            response.raise_for_status()
            vehicle_data = response.json()
            return Vehicle(**vehicle_data)

        except HTTPError as e:
            if e.response.status_code == 404:
                print(f"Vehicle with id {vehicle_id} not found.")
            else:
                print(f"Error: {e}")

    def add_vehicle(self, vehicle: Vehicle):
        try:

            response = requests.post(f"{self.url}/vehicles", json=vehicle.to_dict())
            response.raise_for_status()
            vehicle_data = response.json()
            return Vehicle(**vehicle_data)

        except HTTPError as e:
            if response.status_code == 400:
                print(f"Bad request: {e.response.text}")
            else:
                print(f"Error: {e}")

    def update_vehicle(self, vehicle: Vehicle):
        try:

            response = requests.put(
                f"{self.url}/vehicles/{vehicle.id}", json=vehicle.to_dict()
            )
            response.raise_for_status()
            vehicle_data = response.json()
            return Vehicle(**vehicle_data)

        except HTTPError as e:
            if response.status_code == 400:
                print(f"Bad request: {e.response.text}")
            else:
                print(f"Error: {e}")

    def delete_vehicle(self, id):
        try:

            response = requests.delete(f"{self.url}/vehicles/{id}")
            response.raise_for_status()

        except HTTPError as e:
            if e.response.status_code == 404:
                print(f"Vehicle with id {id} not found.")
            else:
                print(f"Error: {e}")

    def get_distance(self, id1: int, id2: int):
        vehicle1 = self.get_vehicle(id1)
        vehicle2 = self.get_vehicle(id2)
        if vehicle1 and vehicle2:
            return self._haversine(
                vehicle1.latitude,
                vehicle1.longitude,
                vehicle2.latitude,
                vehicle2.longitude,
            )
        return None

    def get_nearest_vehicle(self, id: int):
        target = self.get_vehicle(id)
        if not target:
            return None

        vehicles = self.get_vehicles()
        nearest = None
        min_distance = float("inf")

        for vehicle in vehicles:
            if vehicle.id != target.id:
                distance = self._haversine(
                    target.latitude,
                    target.longitude,
                    vehicle.latitude,
                    vehicle.longitude,
                )
                if distance < min_distance:
                    min_distance = distance
                    nearest = vehicle

        return nearest

    def _haversine(self, lat1, lon1, lat2, lon2):
        R = 6371000
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        a = (
            math.sin(delta_phi / 2) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c

        return distance
