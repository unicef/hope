from collections import namedtuple
from typing import NamedTuple

from steficon.score import Score
from household.models import Household


def hajati(hh: Household):
    # DEMOGRAPHICS
    #  **** Indicator 1.1 - Household Size ****

    pts = Score()
    # pts = PTS()
    pts.hhsize = -2
    if hh.size < 5:
        pts.hhsize = 2
    elif hh.size >= 5 and hh.size < 8:
        pts.hhsize = 0

    # **** Indicator 1.2 - Working Adults ****
    adults = hh.members.filter(age__gte=18, age__lte=65).count()
    working_adult = hh.members.filter(age__gte=18, age__lte=65,
                                      work__in=["fulltime", "seasonal", "parttime"]).count()
    if working_adult >= 1:
        pts.adult = 1
    else:
        pts.adult = -1
    #  **** Indicator 1.3 - Head of Household ****

    head = hh.members.get(relation_to_head=1)
    if head.gender == 'M':
        pts.hhhead = 1
    if head.gender == 'F':
        pts.hhhead = 0
    if head.age > 65 and (working_adult == 0 or adults == 0):
        pts.hhhead = -0.5
    if head.age < 19:
        pts.hhhead = -0.5

    # **** Indicator 1.4 - Foster Child ****
    if hh.members.filter(relation_to_head=13).count() > 0:
        pts.foster = -0.5

    # EDUCATION
    # **** Indicator 2.1 - Out-of-School ****

    return pts.total()
