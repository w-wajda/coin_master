import factory

from app.domain.companies.company import Company
from app.domain.companies.company_schemas import CreateCompanySchema


class CompanyFactory(factory.Factory):
    name = factory.Sequence(lambda n: "Name %03d" % n)
    address = factory.Sequence(lambda n: "Address %03d" % n)

    class Meta:
        model = Company


class CompanyDictFactory(factory.DictFactory):
    name = factory.Sequence(lambda n: "Name %03d" % n)
    address = factory.Sequence(lambda n: "Adrress %03d" % n)

    class Meta:
        model = CreateCompanySchema
