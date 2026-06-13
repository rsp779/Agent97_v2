from __future__ import annotations

import random
from dataclasses import dataclass


def create_faker(seed: int):
    try:
        from faker import Faker  # type: ignore

        fake = Faker()
        fake.seed_instance(seed)
        return fake
    except Exception:
        return LocalFaker(seed)


@dataclass
class LocalFaker:
    seed: int

    def __post_init__(self):
        self.rng = random.Random(self.seed)
        self.first_names = ["Ava", "Mia", "Noah", "Liam", "Emma", "Olivia", "Ethan", "Lucas", "Isha", "Arjun"]
        self.last_names = ["Shah", "Patel", "Khan", "Mehta", "Singh", "Verma", "Iyer", "Nair", "Gupta", "Kapoor"]
        self.domains = ["example.com", "mail.com", "bankmail.com"]
        self.cities = ["Mumbai", "Delhi", "Bengaluru", "Chennai", "Pune", "Hyderabad", "Kolkata", "Ahmedabad"]
        self.states = ["MH", "DL", "KA", "TN", "TS", "WB", "GJ", "UP"]
        self.street_names = ["MG Road", "Park Street", "Jubilee Hills", "Bannerghatta Road", "SG Highway", "Ashram Road"]
        self._counter = 0

    def random_int(self, min: int = 0, max: int = 999999) -> int:
        return self.rng.randint(min, max)

    def uuid4(self) -> str:
        return f"{self.rng.getrandbits(128):032x}"

    def name(self) -> str:
        return f"{self.rng.choice(self.first_names)} {self.rng.choice(self.last_names)}"

    def email(self) -> str:
        name = self.name().lower().replace(" ", ".")
        return f"{name}{self.rng.randint(1,999)}@{self.rng.choice(self.domains)}"

    def phone_number(self) -> str:
        return f"+91-{self.rng.randint(6000000000, 9999999999)}"

    def city(self) -> str:
        return self.rng.choice(self.cities)

    def state(self) -> str:
        return self.rng.choice(self.states)

    def street_address(self) -> str:
        return f"{self.rng.randint(1, 999)} {self.rng.choice(self.street_names)}"

    def postcode(self) -> str:
        return f"{self.rng.randint(100000, 999999)}"

    def company(self) -> str:
        return f"{self.rng.choice(['Prime', 'Vertex', 'Atlas', 'BluePeak', 'Nimbus', 'Axis'])} {self.rng.choice(['Retail', 'Foods', 'Logistics', 'Tech', 'Trade'])}"

    def word(self) -> str:
        return self.rng.choice(["refund", "salary", "invoice", "subscription", "transfer", "cashback", "merchant"])

    def sentence(self, nb_words: int = 8) -> str:
        words = [self.word() for _ in range(nb_words)]
        return " ".join(words).capitalize() + "."

    def date_this_year(self):
        from datetime import date, timedelta

        start = date.today().replace(month=1, day=1)
        return start + timedelta(days=self.rng.randint(0, 180))

