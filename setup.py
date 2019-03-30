from setuptools import setup, find_packages
import os

def requirements():
    with open('requirements.txt') as f:
        raw = f.read()

    return [dependency for dependency in raw.split('\n') if len(dependency)]


if os.environ.get('CI_COMMIT_TAG'):
    version = os.environ['CI_COMMIT_TAG']
else:
    version = os.environ['CI_JOB_ID']

with open('README.md') as f:
    readme = f.read()

setup(
    name="c-lock",
    version=version,
    description="",
    long_description=readme,
    long_description_content_type='text/markdown',
    python_requires=">=3.6",
    author="Javier Junquera Sánchez",
    author_email="javier@junquera.xyz",
    # packages=find_packages(),
    packages=["clockngpn"],
    url="https://gitlab.com/junquera/c-lock",
    license="MIT License",
    install_requires=requirements(),
    tests_require=["pytest"],
    entry_points=dict(
        console_scripts= [
            'c-lockd=clockngpn.cli.server:main',
            'c-lock=clockngpn.cli.client:main'
        ]
    )
)
