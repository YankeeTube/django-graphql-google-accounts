import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

setup(
    name='django-graphql-google-accounts',
    version='0.1',
    packages=['accounts'],
    long_description=README,
    url='https://github.com/YankeeTube/django-graphql-google-accounts',
    author='GM Yankee',
    author_email='subyankee@gmail.com',
    license='MIT',

    install_requires=[
        'django',
        'jwt',
        'requests',
        'graphene',
        'graphene_django',
    ],
)
# python setup.py bdsit_wheel
# twine upload dist/django_graphql_google_accounts-0.2-py3-none-any.whl
