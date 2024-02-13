from setuptools import setup, find_packages

setup(
    name='subprober',
    version='1.0.6',
    author='D. Sanjai Kumar',
    author_email='bughunterz0047@gmail.com',
    description='Subprober - A Fast Probing Tool for Penetration testing',
    packages=find_packages(),
    install_requires=[
        'aiofiles>=23.2.1',
        'aiohttp>=3.9.1' ,
        'alive_progress>=3.1.4' ,
        'beautifulsoup4>=4.11.1' ,
        'colorama>=0.4.6' ,
        'httpx>=0.25.0',
        'Requests>=2.31.0' ,
        'urllib3>=1.26.18'
    ],
    entry_points={
        'console_scripts': [
            'subprober = subprober.subprober:main'
        ]
    },
)