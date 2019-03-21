from setuptools import setup, find_packages


def requirements():
    with open('requirements.txt') as f:
        raw = f.read()

    return [dependency for dependency in raw.split('\n') if len(dependency)]


setup(
    name="clock",
    version="0.0.7",
    author="Javier Junquera Sánchez",
    author_email="javier@junquera.xyz",
    packages=find_packages(),
    url="https://gitlab.com/junquera/c-lock",
    license="LICENSE.txt",
    install_requires=requirements(),
    tests_require=["pytest"],
    entry_points=dict(
        console_scripts= [
            'c-lockd=clock.cli.server:main',
            'c-lock=clock.cli.client:main'
        ]
    )
)
