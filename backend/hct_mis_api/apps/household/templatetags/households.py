from django import template

from hct_mis_api.apps.household.models import IndividualRoleInHousehold

register = template.Library()


@register.simple_tag
def get_extra_roles(individual):
    return IndividualRoleInHousehold.objects.exclude(household=individual.household).filter(individual=individual)

    # return individual.represented_households.exclude(id=individual.household.pk)


@register.simple_tag
def check_(individual):
    return individual.represented_households.exclude(id=individual.household.pk)
