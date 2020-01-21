from django.core.exceptions import ValidationError


class BaseValidator:
    """
    Base validation class, inherit from this class to create custom validators.
    Your custom validators have to implement validation methods that starts
    with name "validate_" so validate can call all the validators from your
    custom validator.

    Custom validate method have to takes *args, **kwargs parameters.

    validate method with parameters have to be called in mutate method.
    If there are validation errors they will be all
    returned as one error message.
    """

    @classmethod
    def validate(cls, excluded_validators=None, *args, **kwargs):
        if not excluded_validators:
            excluded_validators = []

        validate_methods = [
            getattr(cls, m)
            for m in dir(cls)
            if m.startswith("validate_") and m not in excluded_validators
        ]

        errors_list = []
        for method in validate_methods:
            try:
                method(cls, *args, **kwargs)
            except ValidationError as e:
                errors_list.append(e.message)

        if errors_list:
            raise Exception(", ".join(errors_list))


class CommonValidator(BaseValidator):
    def validate_start_end_date(self, start_date, end_date, *args, **kwargs):
        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError(
                    "Start date cannot be greater than the end date."
                )
