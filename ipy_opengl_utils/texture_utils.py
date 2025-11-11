import numpy as np
from PIL import Image
from OpenGL.GL import *

def load_texture(image_path):
    """Loads a texture from an image file and generates an OpenGL texture object."""
    img = Image.open(image_path)
    img_data = img.convert("RGBA").tobytes()
    width, height = img.size

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    glBindTexture(GL_TEXTURE_2D, 0)

    return texture_id

def delete_texture(texture_id):
    """Deletes an OpenGL texture object."""
    glDeleteTextures(1, [texture_id])
