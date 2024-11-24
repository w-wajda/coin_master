import factory

from app.domain.email_templates.email import (
    EmailTemplate,
    EmailTypeEnum,
)


class EmailTemplateFactory(factory.Factory):
    email_type = EmailTypeEnum.WELCOME
    subject = factory.Sequence(lambda n: "Subject %03d" % n)
    text_content = factory.Sequence(lambda n: "Text content %03d" % n)
    html_content = factory.Sequence(lambda n: "Html content %03d" % n)
    is_active = False

    class Meta:
        model = EmailTemplate


class EmailTemplateDictFactory(factory.DictFactory):
    email_type = EmailTypeEnum.WELCOME.name
    subject = factory.Sequence(lambda n: "Subject %03d" % n)
    text_content = factory.Sequence(lambda n: "Text content %03d" % n)
    html_content = factory.Sequence(lambda n: "Html content %03d" % n)
    is_active = False
