import random
from src.app.models import UserReport
from faker import Faker
from sqlalchemy.orm import Session

loc_tolerance = 0.003

fake = Faker()

def generate_heat_map_data(n, lat, lng, weight):
    if weight < 3:
        weight += 3 - weight
    def rand_lat():
        return gen_rand_range(lat, loc_tolerance, 4)
    def rand_lng():
        return gen_rand_range(lng, loc_tolerance, 4)
    def rand_weight():
        return gen_rand_range(weight, 3, 1)
    return [(rand_lat(), rand_lng(), rand_weight()) for _ in range(n)]


def gen_rand_range(center, length, digits=3):
    num = random.uniform(center - length, center + length)
    coeff = 10 ** digits
    return round(num * coeff) / coeff

def gen_fake_user_reports():
    for _ in range(10):
        user_report = UserReport(
            user_id = 1,
            lat=fake.latitude(),
            lng=fake.longitude(),
            radius=fake.random_int(min=1, max=10),
            count=fake.random_int(min=1, max=10),
            comment_ref_id=fake.uuid4(),
            created_at=fake.date_time_between(start_date='-1y', end_date='now')
        )
        session.add(user_report)

    # Commit the changes to the database
    session.commit()

if __name__ == "__main__":
    # gen_fake_user_reports()
    print(fake.factories)