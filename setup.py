"""
Flask-PRISM
-------------

Flask PRISM is a neater way to manage your APIs now and into the future.
"""
from distutils.core import setup

setup(
    name='Flask-PRISM',
    version='0.4.0',
    py_modules=['flask_prism'],
    url='https://github.com/patrickmccallum/flask-prism',
    license='MIT',
    author='Patrick McCallum',
    author_email='vortex@patsnacks.com',
    description='Simple APIs with Flask PRISM',

    zip_safe=False,
    include_package_data=True,
    platforms='any',
    long_description=__doc__,
    install_requires=[
        'Flask'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
