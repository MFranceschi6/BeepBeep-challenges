from setuptools import setup, find_packages
from beepbeep.dataservice import __version__


setup(name='beepbeep-data',
      version=__version__,
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      entry_points="""
      [console_scripts]
      beepbeep-dataservice = beepbeep.dataservice.run:main
      beepbeep-dataservice-challenge = beepbeep.challenge_microservice.challenge:main
      """)
