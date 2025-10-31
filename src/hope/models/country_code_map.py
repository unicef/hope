from django.db import models


class CountryCodeMapManager(models.Manager):
    def __init__(self) -> None:
        self._cache = {2: {}, 3: {}, "ca2": {}, "ca3": {}}
        super().__init__()

    def get_code(self, iso_code: str) -> str | None:
        iso_code = iso_code.upper()
        self.build_cache()
        return self._cache[len(iso_code)].get(iso_code, iso_code)

    def get_iso3_code(self, ca_code: str) -> str:
        ca_code = ca_code.upper()
        self.build_cache()

        return self._cache["ca3"].get(ca_code, ca_code)

    def get_iso2_code(self, ca_code: str) -> str:
        ca_code = ca_code.upper()
        self.build_cache()

        return self._cache["ca2"].get(ca_code, ca_code)

    def build_cache(self) -> None:
        if not self._cache[2] or not self._cache[3] or not self._cache["ca2"] or not self._cache["ca3"]:
            for entry in self.all().select_related("country"):
                self._cache[2][entry.country.iso_code2] = entry.ca_code
                self._cache[3][entry.country.iso_code3] = entry.ca_code
                self._cache["ca2"][entry.ca_code] = entry.country.iso_code2
                self._cache["ca3"][entry.ca_code] = entry.country.iso_code3


class CountryCodeMap(models.Model):
    country = models.OneToOneField("geo.Country", blank=True, null=True, on_delete=models.PROTECT)
    ca_code = models.CharField(max_length=5, unique=True)

    objects = CountryCodeMapManager()

    class Meta:
        app_label = "core"
        ordering = ("country",)

    def __str__(self) -> str:
        return f"{self.country.name} ({self.ca_code})"
