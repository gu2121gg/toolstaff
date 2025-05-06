from setuptools import setup

setup(
    name='toolstaff',
    version='1.0',
    py_modules=['toolstaff'],
    entry_points={
        'console_scripts': [
            'toolstaff=toolstaff:main',
        ],
    },
)
