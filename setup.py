from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name ='behaviortracker',
      version = '0.1',
      description = 'Utilities for working with BehaviorTracker data.',
      url = 'http://github.com/deGravity/BehaviorTracker',
      author = 'Ben Jones',
      author_email = 'bentodjones@gmail.com',
      license = 'MIT',
      packages = ['behaviortracker'],
      install_requires = [
          'pandas',
          'numpy',
          'scipy',
          'plotnine',
          'statsmodels'
      ],
      entry_points = {
          'console_scripts': ['bt=behaviortracker.command_line:main'],
      },
      test_suite = 'nose.collector',
      tests_require = ['nose'],
      zip_safe = False
)