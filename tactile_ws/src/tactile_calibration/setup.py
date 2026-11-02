from setuptools import find_packages, setup

package_name = 'tactile_calibration'

setup(
    name=package_name,
    version='0.2.0',
    packages=find_packages(exclude=['tests']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools', 'numpy', 'scikit-learn', 'PyYAML'],
    zip_safe=True,
    maintainer='Francesco',
    maintainer_email='you@example.com',
    description='Calibration library for the Vanvitelli tactile sensor (PCA, training, export).',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'tactile_train = tactile_calibration.cli:main',
        ],
    },
)
