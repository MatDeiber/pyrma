import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(name ='pyrma',
      version='0.1.4',
      description='Python RMA toolbox',
      long_description=README,
      long_description_content_type="text/markdown",
      packages=['pyrma'],
      author = 'Mathieu Deiber',
      author_email = 'm.deiber@wrl.unsw.edu.au',
      zip_safe=False,
      license="MIT",
      include_package_data=True)