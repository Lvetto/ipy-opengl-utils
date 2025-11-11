from OpenGL.GL import *
import numpy as np

class ShaderProgram:
    def __init__(self, vertex_source, fragment_source, from_str=False):

        if (not from_str):
            self.vertex_shader = self.compile_shader_from_file(vertex_source, GL_VERTEX_SHADER)
            self.fragment_shader = self.compile_shader_from_file(fragment_source, GL_FRAGMENT_SHADER)
        
        else:
            self.vertex_shader = self.compile_shader_from_str(vertex_source, GL_VERTEX_SHADER)
            self.fragment_shader = self.compile_shader_from_str(fragment_source, GL_FRAGMENT_SHADER)
        
        self.program = self.link_shader_program(self.vertex_shader, self.fragment_shader)

        # Clean up shaders after linking
        glDeleteShader(self.vertex_shader)
        glDeleteShader(self.fragment_shader)

    def use(self):
        glUseProgram(self.program)

    def delete(self):
        glDeleteProgram(self.program)

    def set_uniform(self, name, value, dbg_print=False):
        if dbg_print:
            print(f"Setting uniform '{name}' to {value}")

        location = glGetUniformLocation(self.program, name)
        if location == -1:
            # This warning can be noisy, so it's okay to comment out
            # print(f"Warning: Uniform '{name}' not found in shader.")
            return

        # Check for 4x4 matrix first (most specific case)
        if isinstance(value, np.ndarray) and value.shape == (4, 4):
            # glUniformMatrix4fv(location, count, transpose, value)
            glUniformMatrix4fv(location, 1, GL_FALSE, value)

        # Check for vector types (handles list, tuple, or numpy array)
        elif isinstance(value, (list, tuple, np.ndarray)) and len(value) == 4:
            glUniform4fv(location, 1, value)
        elif isinstance(value, (list, tuple, np.ndarray)) and len(value) == 3:
            glUniform3fv(location, 1, value)
            
        # Check for scalar types
        elif isinstance(value, (float)):
            glUniform1f(location, value)
        
        elif isinstance(value, (int)):
            glUniform1i(location, value)

        else:
            raise TypeError(f"Unsupported uniform type for '{name}': {type(value)}")

    def load_source(self, file_path):
        with open(file_path, 'r') as file:
            return file.read()

    def compile_shader_from_file(self, file_path, shader_type):
        shader_source = self.load_source(file_path)
        shader = glCreateShader(shader_type)
        glShaderSource(shader, shader_source)
        glCompileShader(shader)

        success = glGetShaderiv(shader, GL_COMPILE_STATUS)
        if not success:
            error_message = glGetShaderInfoLog(shader)
            glDeleteShader(shader)
            raise Exception(f"Shader Compilation Error: {error_message}")

        return shader
    
    def compile_shader_from_str(self, shader_str, shader_type):
        shader = glCreateShader(shader_type)
        glShaderSource(shader, shader_str)
        glCompileShader(shader)

        success = glGetShaderiv(shader, GL_COMPILE_STATUS)
        if not success:
            error_message = glGetShaderInfoLog(shader)
            glDeleteShader(shader)
            raise Exception(f"Shader Compilation Error: {error_message}")

        return shader

    def link_shader_program(self, vertex_shader, fragment_shader):
        shader_program = glCreateProgram()
        glAttachShader(shader_program, vertex_shader)
        glAttachShader(shader_program, fragment_shader)
        glLinkProgram(shader_program)

        success = glGetProgramiv(shader_program, GL_LINK_STATUS)
        if not success:
            error_message = glGetProgramInfoLog(shader_program)
            glDeleteProgram(shader_program)
            raise Exception(f"Shader Program Linking Error: {error_message}")
        
        return shader_program
