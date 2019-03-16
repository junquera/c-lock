from setuptools import setup, find_packages

setup(
    name="tts",
    tests_require=["pytest"],
    packages=find_packages(),
    entry_points=dict(
        console_scripts= [
            'tts-server=tts.cli.server:main',
            'toc-toc=tts.cli.client:main'
        ]
    )
)
