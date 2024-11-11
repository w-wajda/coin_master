import factory
from geoalchemy2 import WKBElement
from shapely import (
    Point,
    wkt,
)

from app.domain.users.user import User


class UserCreateFactoryDict(factory.DictFactory):
    email = factory.Faker("email")
    password = factory.Faker("password")


class CoordinateProvider:
    def __init__(self, generator):
        self.generator = generator

    def coordinates_point(self) -> WKBElement:
        point = Point(self.generator.latitude(), self.generator.longitude())
        point_wkb = wkt.loads(point.wkt).wkb
        return WKBElement(point_wkb, srid=4326)


factory.Faker.add_provider(CoordinateProvider)


class UserFactory(factory.Factory):
    email = factory.Faker("email")

    is_staff = False

    class Meta:
        model = User

    @factory.post_generation
    def set_password(self: User, create, extracted, **kwargs):
        self.set_password("password")


class ChangePasswordWithTokenDictFactory(factory.DictFactory):
    token = "token123"
    password1 = factory.Faker("password")
    password2 = factory.LazyAttribute(lambda o: o.password1)
