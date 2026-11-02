from setuptools import find_packages, setup

package_name = 'tactile_processing'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Francesco',
    maintainer_email='you@example.com',
    description=(
        'Bridges tactile_core processing math (centroid, geometric zone) '
        'into the ROS2 graph.'
    ),
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'tactile_processing_node = tactile_processing.tactile_processing_node:main',
        ],
    },
)
