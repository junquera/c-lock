from setuptools import setup # find_packages
import os

requirements = [
    'argparse==1.4.0',
    'python-iptables==0.13.0',
    'scapy==2.4.2',
    'pyqrcode==1.2.1'
]

if os.environ.get('CI_COMMIT_TAG'):
    version = os.environ['CI_COMMIT_TAG']
elif os.environ.get('CI_JOB_ID'):
    version = os.environ['CI_JOB_ID']
else:
    version = '0.0.7.2'

with open('README.md') as f:
    readme = f.read()

setup(
    name="c-lock",
    version=version,
    description="A TOTP based next generation port knocking service.",
    long_description=readme,
    long_description_content_type='text/markdown',
    python_requires=">=3.6",
    author="Javier Junquera Sánchez",
    author_email="javier@junquera.xyz",
    # packages=find_packages(),
    packages=["clockngpn", "clockngpn.cli"],
    url="https://gitlab.com/junquera/c-lock",
    license="MIT License",
    install_requires=requirements,
    tests_require=["pytest"],
    entry_points=dict(
        console_scripts= [
            'c-lockd=clockngpn.cli.server:main',
            'c-lock=clockngpn.cli.client:main'
        ]
    )
)
