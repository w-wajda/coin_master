import factory

from app.domain.users.user import User


class UserFactory(factory.Factory):
    email = factory.Faker("email")
    is_staff = False

    class Meta:
        model = User

    @factory.post_generation
    def set_password(self: User, create, extracted, **kwargs):
        self.set_password("password")


class UserCreateFactoryDict(factory.DictFactory):
    email = factory.Faker("email")
    password = factory.Faker("password")
    is_staff = False


class ChangePasswordWithTokenDictFactory(factory.DictFactory):
    token = "token123"
    password1 = factory.Faker("password")
    password2 = factory.LazyAttribute(lambda o: o.password1)
