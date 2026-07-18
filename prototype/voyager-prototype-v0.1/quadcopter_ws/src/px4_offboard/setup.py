from setuptools import setup

package_name = 'px4_offboard'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    install_requires=['setuptools'],
    entry_points={
        'console_scripts': [
            'telemetry_node = px4_offboard.telemetry_node:main',
            'offboard_node = px4_offboard.offboard_node:main',
        ],
    },
)
