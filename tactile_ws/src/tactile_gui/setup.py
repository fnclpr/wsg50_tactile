from setuptools import find_packages, setup

package_name = 'tactile_gui'

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
    description='Minimal PySide6 monitor GUI: live 5x5 tactile heatmap + centroid overlay.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'monitor_gui = tactile_gui.monitor_gui:main',
            'calibration_gui = tactile_gui.calibration_gui:main',
        ],
    },
)
