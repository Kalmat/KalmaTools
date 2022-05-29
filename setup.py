import io
import os
import re
from setuptools import setup, find_packages

scriptFolder = os.path.dirname(os.path.realpath(__file__))
os.chdir(scriptFolder)

# Find version info from module (without importing the module):
with open("kalmatools/__init__.py", "r") as fileObj:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fileObj.read(), re.MULTILINE
    ).group(1)

# Use the README.md content for the long description:
with io.open("README.md", encoding="utf-8") as fileObj:
    long_description = fileObj.read()

setup(
    name='kalmatools',
    version=version,
    url='https://github.com/Kalmat/',
    author='Kalmat',
    author_email='palookjones@gmail.com',
    description=('A simple, cross-platform module with random utilities'),
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='BSD',
    packages=find_packages(where='kalmatools'),
    package_dir={'': 'kalmatools'},
    test_suite='tests',
    install_requires=[
        "beautifulsoup4>=4.10.0",
        "playsound>=1.3.0",
        "plyer>=2.0.0",
        "pygame>=2.0.2",
        "pywinctl",
        "PyQt5>=5.15.4",
        "PyQtWebEngine>=5.15.5",
        "requests>=2.26.0",
        "urllib3>=1.26.7",
        "pywin32>=302; sys_platform == 'win32'",
        "xlib>=0.21; sys_platform == 'linux'",
        "ewmh>=0.1.6; sys_platform == 'linux'",
        "PyUserInput>=0.1.11; sys_platform == 'linux'",
        "fonttools>=4.28.4; sys_platform == 'linux'",
        "pyobjc>=8.1; sys_platform == 'darwin'",
        "fonttools>=4.28.4; sys_platform == 'darwin'"
    ],
    keywords="gui window tools utilities pyqt pygame web url",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications',
        'Environment :: MacOS X',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ],
)
