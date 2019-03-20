from setuptools import setup, find_packages

setup(
    name="clock",
    tests_require=["pytest"],
    packages=find_packages(),
    entry_points=dict(
        console_scripts= [
            'clockd=clock.cli.server:main',
            'clock=clock.cli.client:main'
        ]
    )
)
