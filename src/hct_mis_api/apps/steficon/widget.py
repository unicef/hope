from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

if TYPE_CHECKING:
    from django.db.models.fields import _ChoicesCallable


class ContentTypeChoiceField(forms.ModelChoiceField):
    def __init__(
        self,
        *,
        empty_label: str = "---------",
        required: bool = True,
        widget: Optional[Any] = None,
        label: Optional[Any] = None,
        initial: Optional[Any] = None,
        help_text: str = "",
        to_field_name: Optional[str] = None,
        limit_choices_to: Union[Union[Q, Dict[str, Any]], "_ChoicesCallable", None] = None,
        **kwargs: Any,
    ) -> None:
        queryset = ContentType.objects.order_by("model", "app_label")
        super().__init__(
            queryset,
            empty_label=empty_label,
            required=required,
            widget=widget,
            label=label,
            initial=initial,
            help_text=help_text,
            to_field_name=to_field_name,
            limit_choices_to=limit_choices_to,
            **kwargs,
        )

    def label_from_instance(self, obj: Any) -> str:
        return f"{obj.name.title()} ({obj.app_label})"
