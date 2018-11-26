from setuptools import setup, find_packages
from beepbeep.challenges import __version__


setup(name='beepbeep-challenges',
      version=__version__,
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      entry_points="""
      [console_scripts]
      beepbeep-challenges = beepbeep.challenges.challenges:main
      """)
