from setuptools import setup, find_packages

setup(
    name='ipy-opengl-utils',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A library for rendering OpenGL content in Jupyter notebooks.',
    packages=find_packages(include=['ipy_opengl_utils', 'ipy_opengl_utils.*']),
    install_requires=[
        'numpy',
        'Pillow',
        'pyrr',
        'ipywidgets',
        'ipycanvas',
        'OpenGL',
        'glfw',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)