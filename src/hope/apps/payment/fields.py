from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.postgres.fields import ArrayField


class DynamicChoiceField(forms.MultipleChoiceField):
    def __init__(self, *args: object, **kwargs: object) -> None:
        kwargs.pop("base_field", None)
        kwargs.pop("max_length", None)

        choices_callable = kwargs.pop("choices_callable", None)
        if callable(choices_callable):
            choices = choices_callable()
        else:
            choices = choices_callable or ()

        super().__init__(*args, choices=choices, **kwargs)


class DynamicChoiceArrayField(ArrayField):
    def __init__(self, base_field: object, *args: object, **kwargs: object) -> None:
        self.choices_callable = kwargs.pop("choices_callable", None)
        super().__init__(base_field, *args, **kwargs)

    def formfield(
        self,
        form_class: type[forms.Field] | None = None,
        choices_form_class: type[forms.ChoiceField] | None = None,
        **kwargs: object,
    ) -> object:
        kwargs["choices_callable"] = self.choices_callable
        widget = FilteredSelectMultiple(self.verbose_name, False)
        return super().formfield(
            form_class=form_class or DynamicChoiceField,
            widget=widget,
            **kwargs,
        )
