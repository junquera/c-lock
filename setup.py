from setuptools import setup, find_packages

setup(
    name="clock",
    tests_require=["pytest"],
    packages=find_packages(),
    entry_points=dict(
        console_scripts= [
            'c-lockd=clock.cli.server:main',
            'c-lock=clock.cli.client:main'
        ]
    )
)
