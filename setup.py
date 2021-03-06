from setuptools import setup, find_packages

setup(
    name='athinaweb',
    version='0.97',
    packages=find_packages(),
    scripts=['manage.py'],
    install_requires=['gitpython', 'Django>=3.0', 'djangorestframework', 'python-dateutil',
                      'gunicorn', 'django-registration',
                      'pymysql', 'pyyaml', 'mysqlclient'],
    url='https://github.com/athina-edu/athina-web',
    license='MIT',
    author='Michail Tsikerdekis',
    author_email='Michael.Tsikerdekis@wwu.edu',
    include_package_data=True,
    description=''
)
