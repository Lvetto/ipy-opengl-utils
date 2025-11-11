from OpenGL.GL import *
import glfw
import numpy as np
from PIL import Image
import io

def open_hidden_window(width=100, height=100):
    if not glfw.init():
        raise Exception("GLFW can't be initialized")
    
    glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
    window = glfw.create_window(width, height, "Hidden Context", None, None)

    if not window:
        glfw.terminate()
        raise Exception("GLFW window can't be created")
    
    glfw.make_context_current(window)

    return window

def buffer_setup(width, height):
    # create a framebuffer and bind it
    fbo = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, fbo)

    # create a texture and bind it
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

    # allocate memory to the texture and set scaling parameters
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    # attach the framebuffer to the texture
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, 0)

    # create a render buffer to store depth and stencil data, attach it to the framebuffer
    rbo = glGenRenderbuffers(1)
    glBindRenderbuffer(GL_RENDERBUFFER, rbo)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, width, height)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, rbo)

    if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
        raise RuntimeError("ERROR::FRAMEBUFFER:: Framebuffer is not complete!")

    # unbind the framebuffer
    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    return fbo

def framebuffer_to_image(fbo, width, height):
    # bind the framebuffer
    glBindFramebuffer(GL_FRAMEBUFFER, fbo)

    # read and store buffer data
    glReadBuffer(GL_COLOR_ATTACHMENT0)
    data = glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)
    
    # unbind framebuffer
    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    # create an image from data
    image_data = np.frombuffer(data, dtype=np.uint8).reshape(height, width, 3)
    image_data_flipped = np.flipud(image_data)
    pil_image = Image.fromarray(image_data_flipped)
    
    # save data to a binary memory buffer
    buffer = io.BytesIO()
    pil_image.save(buffer, format='PNG')

    return buffer

def load_texture_pillow(path):
    """Loads an image from a file into an OpenGL texture using Pillow."""
    try:
        img = Image.open(path)
        
        img_data = img.convert("RGBA").tobytes()
        width, height = img.size
        
        texture = glGenTextures(1)
        
        glBindTexture(GL_TEXTURE_2D, texture)
        
        #    - GL_TEXTURE_WRAP_S/T: How to handle coordinates outside [0, 1]
        #    - GL_TEXTURE_MIN/MAG_FILTER: How to filter the texture when scaling
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        
        return texture

    except FileNotFoundError:
        print(f"Error: The file '{path}' was not found.")
        return None

def framebuffer_to_array(fbo, width, height):
    glBindFramebuffer(GL_FRAMEBUFFER, fbo)
    glReadBuffer(GL_COLOR_ATTACHMENT0)
    data = glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)
    glBindFramebuffer(GL_FRAMEBUFFER, 0)
    image_data = np.frombuffer(data, dtype=np.uint8).reshape(height, width, 3)
    image_data_flipped = np.flipud(image_data)
    return image_data_flipped

