from setuptools import setup, find_packages
from beepbeep.challenge_microservice import __version__


setup(name='beepbeep-challenge',
      version=__version__,
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      entry_points="""
      [console_scripts]
      beepbeep-challenges = beepbeep.challenge_microservice.challenge:main
      """)
