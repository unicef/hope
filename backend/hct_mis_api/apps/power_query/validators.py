from django.core.exceptions import ValidationError

from hct_mis_api.apps.power_query.utils import should_run


class FrequencyValidator:
    message = "Invalid frequency"
    code = "invalid"

    def __call__(self, value: str) -> None:
        try:
            should_run(value)
        except BaseException:
            raise ValidationError(self.message, code=self.code, params={"value": value})
