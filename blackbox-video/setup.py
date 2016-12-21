# !/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='blackbox-video',
    packages=find_packages(),
    version='0.1.0',
    description='Blackbox video',
    author='Jeffrey Slort',
    license='MIT',
    author_email='mail@jeffreyslort.nl',
    url='https://github.com/jeff-99/blackbox-webui',
    keywords=['blackbox', 'video' ],
    install_requires= [
        # "opencv2-python",
        # "flask",
        "numpy",
        "click"
    ],
    entry_points={
        'console_scripts': [
            'bbvideo=video.cli:main'
        ]
    },
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