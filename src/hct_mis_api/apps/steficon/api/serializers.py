from hct_mis_api.api.utils import EncodedIdSerializerMixin
from hct_mis_api.apps.steficon.models import Rule, RuleCommit


class RuleSerializer(EncodedIdSerializerMixin):
    class Meta:
        model = Rule
        fields = (
            "id",
            "name",
            "description",
            "type",
        )


class RuleCommitSerializer(EncodedIdSerializerMixin):
    rule = RuleSerializer(read_only=True)

    class Meta:
        model = RuleCommit
        fields = (
            "id",
            "version",
            "rule",
        )
