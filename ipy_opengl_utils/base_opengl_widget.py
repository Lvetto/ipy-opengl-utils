from ipywidgets import DOMWidget
from ipywidgets import Image as IPyImage
from traitlets import Unicode, Int, Bytes, observe
from OpenGL.GL import *
import numpy as np
from PIL import Image
from IPython.display import display
from ipycanvas import Canvas
from ipy_opengl_utils.opengl_utils import open_hidden_window, buffer_setup, framebuffer_to_image, framebuffer_to_array

IP_GL_INIT = None

class BaseOpenglWidget(DOMWidget):
    # Basic properties required by ipywidgets
    _view_name = Unicode('BaseOpenglView').tag(sync=True)
    _model_name = Unicode('BaseOpenglModel').tag(sync=True)
    _view_module = Unicode('baseopenglwidget').tag(sync=True)
    _model_module = Unicode('baseopenglwidget').tag(sync=True)
    _view_module_version = Unicode('^0.1.0').tag(sync=True)
    _model_module_version = Unicode('^0.1.0').tag(sync=True)

    # Widget properties as traitlets to sync with frontend
    width = Int(400).tag(sync=True)
    height = Int(400).tag(sync=True)
    value = Bytes(b'').tag(sync=True)  # Holds PNG image data

    def __init__(self, width=400, height=400, **kwargs):
        super().__init__(**kwargs)
        self.width = width
        self.height = height

        self.image_widget = IPyImage(format='png', width=self.width, height=self.height, description='OpenGL Output')
        self.canvas = Canvas(width=width, height=height)

        self.GL_setup()
        self.update_image()

    def GL_setup(self):
        global IP_GL_INIT
        if not IP_GL_INIT:
            IP_GL_INIT = open_hidden_window()
        
        self.fbo = buffer_setup(self.width, self.height)

        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)

        glViewport(0, 0, self.width, self.height)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glBindFramebuffer(GL_FRAMEBUFFER, 0)
    
    def update_image(self):
        buffer = framebuffer_to_image(self.fbo, self.width, self.height)
        array = framebuffer_to_array(self.fbo, self.width, self.height)
        self.value = buffer.getvalue()
        try:
            self.canvas.clear()
            self.canvas.put_image_data(array, 0, 0)
        except AttributeError:
            pass

    def draw(self, clear_color=(1,1,1,1)):
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        glClearColor(*clear_color)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    @observe('width', 'height')
    def _on_size_change(self, change):
        # React to width/height changes
        self.GL_setup()
        self.update_image()

    def _ipython_display_(self):
        self.draw()
        self.update_image()
        display(self.canvas)
