from setuptools import setup

setup(
    name='references-manager',
    version='1.0.0',
    packages=['references-manager'],
    install_requires=['pyqt5',
                      'PyQtWebEngine',
                      'Flask',
                      'bs4',
                      'requests',
                      'pillow'],
    url='http://www.fabiencollet.com',
    license='MIT',
    author='Fabien Collet',
    author_email='fbncollet@gmail.com',
    description='Web-Based application to organize and display pictures create by and for digital artist'
)