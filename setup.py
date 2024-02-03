from setuptools import setup, find_packages

setup(
    name='oct7_distributor',
    version='0.3',
    packages=find_packages(),
    install_requires=['pydantic >= 2.5.2', 'aiohttp >=3.9.1'],
    # Optional metadata about your package:
    description='Distributor SDK',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/the-social-war/distributor-sdk-python',
)
