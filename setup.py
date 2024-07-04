from setuptools import setup, find_packages

with open("README.md", "r") as streamr:
    long_description = streamr.read()

setup(
    name='subprober',
    version='2.0.0',
    author='D. Sanjai Kumar',
    author_email='bughunterz0047@gmail.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RevoltSecurities/Subprober",
    description='Subprober - An essential HTTP multi-purpose Probing Tool for Penetration Testers and Security Researchers with Asynchronous httpx client support',
    packages=find_packages(),
    install_requires=[
        'aiofiles>=23.2.1',
        'aiohttp>=3.9.1' ,
        'alive_progress>=3.1.4' ,
        'appdirs>=1.4.4',  
        'arsenic>=21.8',
        'beautifulsoup4>=4.11.1',
        'colorama>=0.4.6' ,
        'fake_useragent>=1.2.1', 
        'httpx>=0.25.0',
        'Requests>=2.31.0' ,
        'rich>=13.7.1' ,
        'structlog>=20.2.0' ,  
        'urllib3>=1.26.18',
        'anyio>=4.2.0',
        'uvloop>=0.19.0',
        'pyjarm>=0.0.5'
    ],
    entry_points={
        'console_scripts': [
            'subprober = subprober.subprober:main'
        ]
    },
)
