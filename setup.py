from setuptools import setup

setup(
    name='unturned note generator',
    version='0.1.0',
    author="khakers",
    py_modules=['note-generator', 'config'],
    install_requires=[
        'Click',
        'rich',
        'pyyaml',
        'marshmallow',
        'marshmallow-dataclass',
        'jinja2',
        'pathvalidate'
    ],
    data_files=['templates'],
    entry_points={
        'console_scripts': [
            'notegen = notegenerator:build',
        ],
    },
)
