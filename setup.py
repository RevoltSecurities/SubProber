from setuptools import setup, find_packages

setup(
    name='subprober',
    version='1.0.1',
    author='D. Sanjai Kumar',
    author_email='bughunterz0047@gmail.com',
    description='Subrpober - A http protocol probing tool',
    packages=find_packages(),
    install_requires=[
        'colorama==0.4.4',
        'httpx==0.25.0',
        'requests==2.31.0',
        'argparse==1.4.0',
        'beautifulsoup4==4.11.1',
    ],
    entry_points={
        'console_scripts': [
            'subprober = subprober.subprober:main'
        ]
    },
)