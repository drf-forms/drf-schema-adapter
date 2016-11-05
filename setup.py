import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='drf_auto_endpoint',
    version='0.9.9',
    packages=['drf_auto_endpoint'],
    include_package_data=True,
    license='MIT License',
    description='Package description',
    long_description=README,
    url='https://bitbucket.org/levit_scs/drf_auto_endpoint',
    author='LevIT',
    author_email='info@levit.be',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'Django>=1.9,<1.10',
        'djangorestframework>=3.3.3,<4.0.0',
        'django-filter>=0.13.0',
        'Inflector>=2.0.11',
    ]
)
