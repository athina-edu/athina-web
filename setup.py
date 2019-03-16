from setuptools import setup, find_packages

setup(
    name='athinaweb',
    version='0.9',
    packages=find_packages(),
    scripts=['manage.py'],
    install_requires=['gitpython', 'Django>=2.0,<3.0', 'djangorestframework', 'django-registration-redux',
                      'python-dateutil'],
    url='https://github.com/athina-edu/athina-web',
    license='MIT',
    author='Michail Tsikerdekis',
    author_email='Michael.Tsikerdekis@wwu.edu',
    description=''
)
