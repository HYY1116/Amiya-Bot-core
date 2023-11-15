import os
import json
import setuptools
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel

from urllib import request

def ver_num(_v):
    num = int(_v.replace('.', ''))
    if num < 1000:
        num *= 10
    return num

def get_new_version():
    pypi = json.loads(request.urlopen('https://pypi.python.org/pypi/amiyabot/json').read())
    v_list = {ver_num(v): v for v in pypi['releases'].keys()}
    s_list = sorted(v_list)
    latest = v_list[s_list[-1]]

    print(f'latest: {latest}')

    return f"{latest}"
    # return f"1.10.10"

# Auto increment the version number.
# 1.0.9 -> 1.1.0 , 1.9.9 -> 2.0.0 but 9.9.9 -> 10.0.0
def incr_version(v):
    v = v.split('.')
    if len(v) == 3:
        if int(v[2]) >= 9:
            v[2] = '0'
            if int(v[1]) >= 9:
                v[1] = '0'
                v[0] = str(int(v[0]) + 1)
            else:
                v[1] = str(int(v[1]) + 1)
        else:
            v[2] = str(int(v[2]) + 1)
    else:
        v.append('1')
    return '.'.join(v)

class CustomBdistWheelCommand(_bdist_wheel):
    user_options = _bdist_wheel.user_options + [
        ('auto-increment-version', None, 'Auto increment the version number before building with special rule: 1.0.9 -> 1.1.0 , 1.9.9 -> 2.0.0 . However 9.9.9 -> 10.0.0')
    ]

    def initialize_options(self):
        _bdist_wheel.initialize_options(self)
        self.auto_increment_version = False

    def finalize_options(self):
        _bdist_wheel.finalize_options(self)
        latest_version = get_new_version()
        if self.auto_increment_version:
            new_version = incr_version(latest_version)
            print(f'Auto-incrementing version to: {new_version}')
            self.distribution.metadata.version = new_version
        else:
            new_version = incr_version(latest_version)
            release_new = input(f'new?: {new_version} (Y/n)')

            if not (not release_new or release_new.lower() == 'y'):
                new_version = input('version: ')

        self.distribution.metadata.version = new_version

    def run(self):
        _bdist_wheel.run(self)

with open('README.md', mode='r', encoding='utf-8') as md:
    description = md.read()

with open('requirements.txt', mode='r', encoding='utf-8') as req:
    requirements = sorted(req.read().lower().strip('\n').split('\n'))

with open('requirements.txt', mode='w', encoding='utf-8') as req:
    req.write('\n'.join(requirements))

data_files = []
for root, dirs, files in os.walk('amiyabot/_assets'):
    for item in files:
        data_files.append(os.path.join(root, item))

setuptools.setup(
    name='amiyabot-core-test',
    version="0.0.1",
    author='vivien8261',
    author_email='826197021@qq.com',
    url='https://www.amiyabot.com',
    license='MIT Licence',
    description='Python 异步渐进式机器人框架',
    long_description=description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(include=['amiyabot', 'amiyabot.*']),
    data_files=[('amiyabot', data_files)],
    include_package_data=True,
    python_requires='>=3.8',
    install_requires=requirements,
    cmdclass={
        'bdist_wheel': CustomBdistWheelCommand,
    },
)

# python setup.py bdist_wheel --auto-increment-version
