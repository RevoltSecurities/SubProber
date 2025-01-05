from setuptools import setup, find_packages

with open("README.md", "r") as streamr:
    long_description = streamr.read()


setup(
    name='subprober',
    version='3.0.0',
    author='D. Sanjai Kumar',
    author_email='bughunterz0047@gmail.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RevoltSecurities/Subprober",
    description='Subprober - An essential HTTP multi-purpose Probing Tool for Penetration Testers and Security Researchers with Asynchronous httpx client support',
    packages=find_packages(),
    install_requires=[
        'aiodns>=3.2.0',
        'aiofiles>=24.1.0',
        'aiojarm>=0.2.2',
        'alive_progress>=3.2.0',
        'appdirs>=1.4.4',
        'art>=6.4',
        'asynciolimiter>=1.1.1',
        'beautifulsoup4>=4.12.3',
        'colorama>=0.4.6',
        'cryptography>=44.0.0',
        'fake_useragent>=1.5.1',
        'httpx>=0.28.1',
        'mmh3>=5.0.1',
        'playwright>=1.49.1',
        'Requests>=2.32.3',
        'rich>=13.9.4',
        'setuptools>=75.2.0',
        'simhash>=2.1.2',
        'urllib3>=1.26.18',
        'uvloop>=0.21.0',
        'websockets>=14.1'
    ],
    entry_points={
        'console_scripts': [
            'subprober = subprober.subprober:main'
        ]
    },
)
