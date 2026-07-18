from setuptools import setup
import os
from glob import glob

package_name = 'custom_uav_stack'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'gcs'), glob('custom_uav_stack/gcs/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Vaibhav',
    maintainer_email='vaibhav@iitm.ac.in',
    description='Custom flight stack: physics engine simulator, PID controller, and GCS bridge',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'simulator_node = custom_uav_stack.simulator_node:main',
            'controller_node = custom_uav_stack.controller_node:main',
            'gcs_bridge_node = custom_uav_stack.gcs_bridge_node:main',
        ],
    },
)
