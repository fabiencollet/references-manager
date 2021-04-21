from setuptools import setup

setup(
    name='references-manager',
    version='0.1.0',
    install_requires=['pyqt5>=5.14.5',
                      'PyQtWebEngine>=5.14.5',
                      'Flask>=1.1.2',
                      'bs4>=0.0.1',
                      'requests>=2.22.0',
                      'pillow>=7.0.0'], 
                      
    python_requires='>=3.6',
    
    url='http://www.fabiencollet.com',
    license='MIT',
    author='Fabien Collet',
    author_email='fbncollet@gmail.com',
    description='Web-Based application to organize and display pictures create by and for digital artist',
)
