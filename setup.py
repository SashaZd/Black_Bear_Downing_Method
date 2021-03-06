# from setuptools import setup
# from distutils.core import setup

setup(
	name='Black_Bear_Downing_Method',
	version="1.0.1a",
	description="Population reconstruction of black bears using harvest data.",
	# long_description=open('README.md').read(),
	author="Shefali Azad",
	author_email="azadshefali@gmail.com",
	maintainer="Sasha Azad",
	maintainer_email="sasha.azad@gatech.edu",
	url="https://github.com/SashaZd/Black_Bear_Downing_Method",
	install_requires=[
 		'xlrd',
 		'xlwt',
 		'xlutils'
	]
)