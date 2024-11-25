import factory

from app.domain.companies.company_factory import CompanyFactory, CompanyDictFactory
from app.domain.receipts.receipt import Receipt
from app.domain.users.user_factory import (
    UserDictFactory,
    UserFactory,
)


class ReceiptFactory(factory.Factory):
    amount = factory.Sequence(lambda n: "%.2f" % (n + 1 + 0.99))
    scan_file = factory.Sequence(lambda n: "Scan file %03d" % n)
    company = factory.SubFactory(CompanyFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = Receipt


class ReceiptDictFactory(factory.DictFactory):
    amount = factory.Sequence(lambda n: "%.2f" % (n + 1 + 0.99))
    scan_file = factory.Sequence(lambda n: "Scan file %03d" % n)
    company = factory.SubFactory(CompanyDictFactory)
    user = factory.SubFactory(UserDictFactory)