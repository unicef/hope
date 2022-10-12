import logging
from typing import List, Optional

from queryset_sequence import ModelIterable, QuerySetSequence

logger = logging.getLogger(__name__)


class ExtendedQuerySetSequence(QuerySetSequence):
    def _clone(self):
        clone = ExtendedQuerySetSequence(*[qs._clone() for qs in self._querysets])
        clone._queryset_idxs = self._queryset_idxs
        clone._order_by = self._order_by
        clone._fields = self._fields
        clone._standard_ordering = self._standard_ordering
        clone._low_mark = self._low_mark
        clone._high_mark = self._high_mark
        clone._iterable_class = self._iterable_class
        clone.model = self.model

        return clone

    def aggregate(self, *args, **kwargs) -> dict:
        results_dict = {}

        aggregated_querysets: List[dict] = [qs.aggregate(*args, **kwargs) for qs in self._querysets]
        keys = list(aggregated_querysets[0].keys())
        for key in keys:
            values = [qs.get(key, None) for qs in aggregated_querysets]
            results_dict[key] = sum(list(filter(lambda x: x is not None, values)))

        return results_dict

    def merge_by(
        self, merge_field, aggregated_fields: Optional[List[str]] = None, regular_fields: Optional[List[str]] = None
    ) -> List[dict]:
        """Merge grouped_by + annotated querysets"""
        aggregated_fields = aggregated_fields or []
        regular_fields = regular_fields or []
        results_list = []

        object_list = list(self.values(merge_field, *aggregated_fields, *regular_fields))
        # make unique and maintain order
        merge_unique_field_values = list(dict.fromkeys([obj[merge_field] for obj in object_list]))

        for merge_field_value in merge_unique_field_values:
            merged_object = {merge_field: merge_field_value}
            objects = [obj for obj in object_list if obj.get(merge_field) == merge_field_value]

            for annotated_field_name in aggregated_fields:
                annotated_field_values = [obj.get(annotated_field_name) for obj in objects]
                merged_object[annotated_field_name] = sum(list(filter(lambda x: x is not None, annotated_field_values)))

            for regular_field_name in regular_fields:
                merged_object[regular_field_name] = objects[0][regular_field_name]

            results_list.append(merged_object)

        return results_list

    def distinct(self, *fields):
        clone = super().distinct(*fields)

        if clone._iterable_class != ModelIterable:
            clone._querysets = [clone._querysets[0].union(*clone._querysets[1:])]

        return clone
