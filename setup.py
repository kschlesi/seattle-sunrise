from setuptools import setup
import glob

setup(
    name = "seattle_sunrise",
    version = "0.0.0",
    packages = ['seattle_sunrise'],
    scripts = glob.glob('./bin/*'),
    install_requires = [
        'requests',
        'PyYAML',
    ],
    url='https://github.com/kschlesi/seattle-sunrise',
)
