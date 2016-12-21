# !/usr/bin/env python

from setuptools import setup
setup(
    name='blackbox-webui',
    packages=['app'],
    version='0.1.0',
    description='Blackbox web UI',
    author='Jeffrey Slort',
    license='MIT',
    author_email='mail@jeffreyslort.nl',
    url='https://github.com/jeff-99/blackbox-webui',
    keywords=['blackbox', 'flask', 'package', ],
    install_requires = [
        'flask'
    ],
    # entry_points={
    #     'console_scripts': [
    #         '{{ cookiecutter.project_slug }}={{ cookiecutter.project_slug }}.cli:main'
    #     ]
    # },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development',
    ],
)