from setuptools import setup, find_packages

setup(
    name='athinaweb',
    version='0.9',
    packages=find_packages(),
    scripts=['manage.py'],
    install_requires=['gitpython'],
    url='https://github.com/athina-edu/athina-web',
    license='MIT',
    author='Michail Tsikerdekis',
    author_email='Michael.Tsikerdekis@wwu.edu',
    description=''
)