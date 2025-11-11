from pyrr import Matrix44
import numpy as np

class Camera:
    def __init__(self, position=(0, 0, 20), target=(0, 0, 0), up=(0, 1, 0), fov=45.0, aspect=1.0, near=0.1, far=500.0):
        self.position = np.array(position, dtype=np.float32)
        self.target = np.array(target, dtype=np.float32)
        self.up = np.array(up, dtype=np.float32)
        self.fov = fov
        self.aspect = aspect
        self.near = near
        self.far = far

        self.yaw = 0.0
        self.pitch = 0.0
        self._update_direction()

    def set_rotation(self, pitch, yaw):
        self.pitch = pitch
        self.yaw = yaw
        self._update_direction()

    def _update_direction(self):
        yaw_rad = np.radians(self.yaw)
        pitch_rad = np.radians(self.pitch)

        direction = np.array([
            np.cos(pitch_rad) * np.cos(yaw_rad),
            np.sin(pitch_rad),
            np.cos(pitch_rad) * np.sin(yaw_rad)
        ], dtype=np.float32)
        direction = direction / np.linalg.norm(direction)
        self.target = self.position + direction

    def get_view_matrix(self):
        return Matrix44.look_at(
            eye=self.position,
            target=self.target,
            up=self.up
        )

    def get_projection_matrix(self):
        return Matrix44.perspective_projection(
            self.fov, self.aspect, self.near, self.far
        )
    
    def orbit(self, center, radius, pitch=None, yaw=None):
        if pitch is not None:
            self.pitch = pitch
        if yaw is not None:
            self.yaw = yaw

        yaw_rad = np.radians(self.yaw)
        pitch_rad = np.radians(self.pitch)

        x = center[0] + radius * np.cos(pitch_rad) * np.cos(yaw_rad)
        y = center[1] + radius * np.sin(pitch_rad)
        z = center[2] + radius * np.cos(pitch_rad) * np.sin(yaw_rad)

        self.position = np.array([x, y, z], dtype=np.float32)
        self.target = np.array(center, dtype=np.float32)
