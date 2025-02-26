from django.db import models

import json


class Country(models.Model):
    name = models.CharField(max_length=100)
    alpha2Code = models.CharField(max_length=2)
    alpha3Code = models.CharField(max_length=3)
    population = models.IntegerField()

    top_level_domains_json = models.TextField(null=True, blank=True)
    capital = models.CharField(max_length=100, null=True, blank=True)

    region = models.ForeignKey(
        "Region",
        on_delete=models.CASCADE,
        related_name="countries",
    )

    def __str__(self):
        return self.name

    @property
    def top_level_domains(self):
        """Get the top level domains as a list."""
        if not self.top_level_domains_json:
            return []
        return json.loads(self.top_level_domains_json)
    
    @top_level_domains.setter
    def top_level_domains(self, value):
        """Set the top level domains from a list."""
        if value is None:
            self.top_level_domains_json = None
        else:
            self.top_level_domains_json = json.dumps(value)


class Region(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
