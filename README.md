# ipy-opengl-utils

## Overview

`ipy-opengl-utils` is a Python library designed to facilitate the use of OpenGL in Jupyter notebooks. It provides a set of utilities for rendering 3D graphics, managing shaders, handling textures, and manipulating meshes. This library aims to simplify the integration of OpenGL into interactive notebook environments, making it easier for users to create and visualize 3D content.

## Features

- **OpenGL Widget**: A customizable widget for rendering OpenGL content directly in Jupyter notebooks.
- **Shader Utilities**: Functions for loading, compiling, and linking OpenGL shaders.
- **Mesh Utilities**: Tools for generating and manipulating 3D meshes, including spheres and other geometric shapes.
- **Camera Management**: A Camera class for handling view and projection transformations.
- **Texture Management**: Functions for loading textures from image files and managing OpenGL texture objects.

## Installation

To install `ipy-opengl-utils`, clone the repository and install the required dependencies:

```bash
git clone https://github.com/yourusername/ipy-opengl-utils.git
cd ipy-opengl-utils
pip install -r requirements.txt
```

## Usage

Here is a simple example of how to use the `ipy-opengl-utils` library in a Jupyter notebook:

```python
from ipy_opengl_utils.particle_widget import ParticleWidget

# Create an instance of the OpenGL widget
widget = ParticleWidget(width=800, height=600)

# Display the widget
display(widget)
```

For more detailed examples, please refer to the `examples/demo_notebook.ipynb` file.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
