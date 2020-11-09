
class Score:
    def __init__(self):
        self.hhsize = 0
        self.adult = 0
        self.hhhead = 0
        self.foster = 0

    def total(self):
        return self.hhhead + self.hhsize + self.adult + self.foster

#
# {% elif hh.size >= 5 and  hh.size < 8 %}
# {% set pts.hhsize 0 -%}
# {% else %}
# {% set pts.hhsize = -2 -%}
