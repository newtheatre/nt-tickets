from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify
from tickets import models


class Command(BaseCommand):
  help = 'Create default categories when launching a new database'

  categories = ['In House', 'Fringe', 'External', 'StuFF', 'StuFF Events']

  def cat(self, cname, sort):
    if not models.Category.objects.filter(name=cname).exists():
      models.Category.objects.create(name=cname, slug=slugify(cname), sort=sort)

  def handle(self, *args, **options):
    for i, category in enumerate(self.categories):
      self.cat(cname=category, sort=i+1)
