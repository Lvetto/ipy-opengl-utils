# filepath: /ipy-opengl-utils/ipy-opengl-utils/ipy_opengl_utils/mesh_utils.py
import numpy as np

def generate_sphere_mesh(radius=1.0, stacks=16, slices=16):
    vertices = []
    indices = []

    for i in range(stacks + 1):
        theta = np.pi * i / stacks
        sin_theta = np.sin(theta)
        cos_theta = np.cos(theta)

        for j in range(slices + 1):
            phi = 2 * np.pi * j / slices
            sin_phi = np.sin(phi)
            cos_phi = np.cos(phi)

            x = cos_phi * sin_theta
            y = cos_theta
            z = sin_phi * sin_theta
            vertices.append(radius * np.array([x, y, z]))

    for i in range(stacks):
        for j in range(slices):
            first = (i * (slices + 1)) + j
            second = first + slices + 1
            indices.append(first)
            indices.append(second)
            indices.append(first + 1)
            indices.append(second)
            indices.append(second + 1)
            indices.append(first + 1)

    vertices = np.array(vertices, dtype=np.float32)
    indices = np.array(indices, dtype=np.uint32)
    return vertices, indices

def generate_cube_mesh(size=1.0):
    vertices = np.array([
        # Front face
        -size, -size, size,
         size, -size, size,
         size,  size, size,
        -size,  size, size,
        # Back face
        -size, -size, -size,
        -size,  size, -size,
         size,  size, -size,
         size, -size, -size,
    ], dtype=np.float32)

    indices = np.array([
        0, 1, 2, 2, 3, 0,  # Front face
        4, 5, 6, 6, 7, 4,  # Back face
        0, 1, 7, 7, 4, 0,  # Left face
        2, 3, 6, 6, 5, 2,  # Right face
        3, 0, 4, 4, 6, 3,  # Top face
        1, 2, 5, 5, 7, 1   # Bottom face
    ], dtype=np.uint32)

    return vertices, indices