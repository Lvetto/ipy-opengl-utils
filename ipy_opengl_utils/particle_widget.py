from ipy_opengl_utils.base_opengl_widget import BaseOpenglWidget
from ipy_opengl_utils.shader_utils import ShaderProgram
from ipy_opengl_utils.camera import Camera
from ipy_opengl_utils.mesh_utils import generate_sphere_mesh
from ipy_opengl_utils.opengl_utils import framebuffer_to_array
from ipy_opengl_utils.math_utils import unproject_ray, ray_sphere_intersect
from OpenGL.GL import *
import numpy as np
import time
import os

class ParticleWidget(BaseOpenglWidget):
    def __init__(self, width, height, select_particles=False, draw_axes=False):
        super().__init__(width, height)

        shader_dir = os.path.join(os.path.dirname(__file__), "shaders")
        self.shader = ShaderProgram(
            vertex_source=os.path.join(shader_dir, "vertex_shader.glsl"),
            fragment_source=os.path.join(shader_dir, "fragment_shader.glsl")
        )
        self.line_shader = ShaderProgram(
            vertex_source=os.path.join(shader_dir, "line_vertex_shader.glsl"),
            fragment_source=os.path.join(shader_dir, "line_fragment_shader.glsl")
        )
        
        self.camera = Camera(position=(0, 0, 20), aspect=width/height)
        self.view = self.camera.get_view_matrix()
        self.projection = self.camera.get_projection_matrix()

        self.positions = np.array([], dtype=np.float32)
        self.colors = np.array([], dtype=np.float32)
        
        self.sphere_vao = None
        self.sphere_vbo = None
        self.sphere_ebo = None
        self.instance_vbo = None
        self.color_vbo = None
        self.index_count = 0
        self._dragging = False

        self._redraw_pending = False
        self._last_redraw = 0
        self._redraw_interval = 1 / 60

        self.yaw = 45.0
        self.pitch = 30.0
        self.radius = 20.0

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glFrontFace(GL_CW)

        self.canvas.on_mouse_down(self._on_mouse_down)
        self.canvas.on_mouse_up(self._on_mouse_up)
        self.canvas.on_mouse_move(self._on_mouse_move)
        self.canvas.on_mouse_wheel(self._on_wheel)

        self.select_particles = select_particles
        self.selection_index = -1

        self.draw_axes = draw_axes

        self.setup_axes()
        self.setup_sphere_buffers()
        self.camera_setup()

    def _on_mouse_down(self, x, y):
        self._dragging = True
        self._last_mouse = (x, y)

    def _on_mouse_up(self, x, y):
        self._dragging = False
        self._last_mouse = None

    def _on_mouse_move(self, x, y):
        if self._dragging and self._last_mouse is not None:
            dx = x - self._last_mouse[0]
            dy = y - self._last_mouse[1]

            self.yaw += dx * 0.5
            self.pitch += dy * 0.5
            self.pitch = max(-89, min(89, self.pitch))

            self.camera.orbit(self.center, radius=self.radius, pitch=self.pitch, yaw=self.yaw)

            #self.draw()
            #self.update_image()
            self._throttled_draw()
            self._last_mouse = (x, y)
        
        elif self.select_particles:
            self._pick_particle(x, y)
 
    def _pick_particle(self, x, y):
        # Convert (x, y) to normalized device coordinates
        ndc_x = (2.0 * x) / self.width - 1.0
        y_flipped = self.height - y
        ndc_y = (2.0 * y_flipped) / self.height - 1.0

        # Unproject to get ray in world space
        ray_origin, ray_dir = unproject_ray(ndc_x, ndc_y, self.camera)
        min_dist = float('inf')
        selected = -1
        for i, pos in enumerate(self.positions):
            hit, dist = ray_sphere_intersect(ray_origin, ray_dir, pos, 1.0)  # 1.0 = sphere radius
            if hit and dist < min_dist:
                min_dist = dist
                selected = i

        if selected >= 0 and selected != self.selection_index:
            self._throttled_draw()
        
        self.selection_index = selected

    def _on_wheel(self, delta_x, delta_y):
        self.radius += delta_y * 0.1
        self.radius = max(1.0, self.radius)
        self.camera.orbit(self.center, radius=self.radius, pitch=self.pitch, yaw=self.yaw)
        self._throttled_draw()
    
    def camera_setup(self):
        if len(self.positions) == 0:
            center = np.array([0.0, 0.0, 0.0], dtype=np.float32)
            self.center = center
            self.camera.orbit(center, radius=self.radius, pitch=self.pitch, yaw=self.yaw)
            return

        center = np.mean(self.positions, axis=0)
        self.center = center
        self.camera.orbit(center, radius=self.radius, pitch=self.pitch, yaw=self.yaw)

    def update_particles(self):
        pass

    def add_particles(self, positions, colors, update_cam=False):
        if len(self.positions) == 0:
            self.positions = positions
            self.colors = colors
            self.setup_sphere_buffers()
        
        else:
            # Append new particle positions to existing ones
            self.positions = np.concatenate((self.positions, positions), axis=0)
            self.colors = np.concatenate((self.colors, colors), axis=0)
            self.setup_sphere_buffers()

        if update_cam:
            self.camera_setup()

    def setup_sphere_buffers(self, radius=1.0, stacks=16, slices=16):
        # Generate sphere mesh
        vertices, indices = generate_sphere_mesh(radius, stacks, slices)
        self.index_count = len(indices)

        # Create VAO, VBO, EBO for sphere mesh
        self.sphere_vao = glGenVertexArrays(1)
        self.sphere_vbo = glGenBuffers(1)
        self.sphere_ebo = glGenBuffers(1)

        glBindVertexArray(self.sphere_vao)

        # Vertex positions
        glBindBuffer(GL_ARRAY_BUFFER, self.sphere_vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        # Indices
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.sphere_ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

        # Instance positions buffer (will be updated each frame)
        self.instance_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.instance_vbo)
        # Allocate empty buffer for now
        glBufferData(GL_ARRAY_BUFFER, len(self.positions) * 4, None, GL_DYNAMIC_DRAW)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribDivisor(1, 1)  # Advance per instance

        # Instance colors buffer
        self.color_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.color_vbo)
        glBufferData(GL_ARRAY_BUFFER, self.colors.nbytes, self.colors, GL_DYNAMIC_DRAW)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
        glEnableVertexAttribArray(2)
        glVertexAttribDivisor(2, 1)  # Advance per instance

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def uniform_setup(self, light_pos=(50.0, 50.0, 100.0), light_color=(1.0, 1.0, 1.0), material_color=(0.8, 0.2, 0.2)):
        self.shader.set_uniform("view", self.camera.get_view_matrix())
        self.shader.set_uniform("projection", self.camera.get_projection_matrix())
        self.shader.set_uniform("lightPos", light_pos)
        self.shader.set_uniform("lightColor", light_color)
        self.shader.set_uniform("viewPos", self.camera.position)
        self.shader.set_uniform("materialColor", material_color)

    def _throttled_draw(self):
        now = time.monotonic()
        if now - self._last_redraw > self._redraw_interval:
            self.draw()
            self._last_redraw = now
        
        else:
            pass

    def setup_axes(self, position=(0,0,0), scale=1.0):
        line_vertices = np.array([[0, 0, 0], [1, 0, 0],
                                      [0, 0, 0], [0, 1, 0],
                                      [0, 0, 0], [0, 0, 1]], dtype=np.float32)
        
        line_vertices += np.array(position, dtype=np.float32)
        line_vertices *= scale

        self.axes_verts = line_vertices

        self.axes_vao = glGenVertexArrays(1)
        self.axes_vbo = glGenBuffers(1)
        glBindVertexArray(self.axes_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.axes_vbo)
        glBufferData(GL_ARRAY_BUFFER, line_vertices.nbytes, line_vertices, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

    def draw(self, draw_particles=True, draw_axes=False):
        super().draw((0.8, 0.8, 0.8, 1))

        if draw_particles:
            self.shader.use()

            self.uniform_setup()
            self.shader.set_uniform("selectionIndex", self.selection_index)
            self.shader.set_uniform("isLine", False)  # <--- Not a line for spheres

            # Prepare instance positions
            glBindBuffer(GL_ARRAY_BUFFER, self.instance_vbo)
            glBufferData(GL_ARRAY_BUFFER, self.positions.nbytes, self.positions, GL_DYNAMIC_DRAW)

            # Bind VAO and draw instances
            glBindVertexArray(self.sphere_vao)
            glDrawElementsInstanced(GL_TRIANGLES, self.index_count, GL_UNSIGNED_INT, None, len(self.positions))
            glBindVertexArray(0)
        
        if self.draw_axes or draw_axes:
            glBindBuffer(GL_ARRAY_BUFFER, self.axes_vbo)
            glBufferData(GL_ARRAY_BUFFER, self.axes_verts.nbytes, self.axes_verts, GL_STATIC_DRAW)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
            glEnableVertexAttribArray(0)

            self.line_shader.use()
            self.line_shader.set_uniform("view", self.camera.get_view_matrix())
            self.line_shader.set_uniform("projection", self.camera.get_projection_matrix())

            glLineWidth(3.0)

            self.line_shader.set_uniform("lineColor", (1.0, 0.0, 0.0))  # X axis - red
            glDrawArrays(GL_LINES, 0, 2)

            self.line_shader.set_uniform("lineColor", (0.0, 1.0, 0.0))  # Y axis - green
            glDrawArrays(GL_LINES, 2, 2)

            self.line_shader.set_uniform("lineColor", (0.0, 0.0, 1.0))  # Z axis - blue
            glDrawArrays(GL_LINES, 4, 2)
            glBindVertexArray(0)

        # Update the canvas with the new image
        img_array = framebuffer_to_array(self.fbo, self.width, self.height)
        self.canvas.put_image_data(img_array, 0, 0)
