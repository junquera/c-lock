from setuptools import setup, find_packages


def requirements():
    with open('requirements.txt') as f:
        raw = f.read()

    return [dependency for dependency in raw.split('\n') if len(dependency)]


with open('README.md') as f:
    readme = f.read()

setup(
    name="c-lock",
    version="0.0.7.1",
    description="",
    long_description=readme,
    long_description_content_type='text/markdown',
    python_requires=">=3.6",
    author="Javier Junquera Sánchez",
    author_email="javier@junquera.xyz",
    # packages=find_packages(),
    packages=["clock"],
    url="https://gitlab.com/junquera/c-lock",
    license="MIT License",
    install_requires=requirements(),
    tests_require=["pytest"],
    entry_points=dict(
        console_scripts= [
            'c-lockd=clock.cli.server:main',
            'c-lock=clock.cli.client:main'
        ]
    )
)
