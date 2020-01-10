from django.core.exceptions import ValidationError


class BaseValidator:
    """
    Base validation class, inherit from this class to create custom validators.
    Your custom validators have to implement validation methods that starts
    with name "validate_" so validate can call all the validators from your
    custom validator.

    Custom validate method have to takes *args, **kwargs parameters.

    Custom Validator Class needs to be initialized and validate method with
    parameters have to be called in mutate method. If there are validation
    errors they will be all returned as error message.
    """

    def validate(self, *args, **kwargs):
        validate_methods = [
            getattr(self, m) for m in dir(self) if m.startswith('validate_')
        ]

        errors_list = []
        for method in validate_methods:
            try:
                method(self, *args, **kwargs)
            except ValidationError as e:
                errors_list.append(e.message)

        if errors_list:
            raise Exception(', '.join(errors_list))
