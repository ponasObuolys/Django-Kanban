from django import get_version
from packaging import version

def get_django_version():
    return version.parse(get_version()) 