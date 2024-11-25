import factory

from app.domain.companies.company import Company
from app.domain.users.user_factory import (
    UserDictFactory,
    UserFactory,
)


class CompanyFactory(factory.Factory):
    name = factory.Sequence(lambda n: "Name %03d" % n)
    address = factory.Sequence(lambda n: "Address %03d" % n)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = Company


class CompanyDictFactory(factory.DictFactory):
    name = factory.Sequence(lambda n: "Name %03d" % n)
    address = factory.Sequence(lambda n: "Address %03d" % n)
    user = factory.SubFactory(UserDictFactory)
