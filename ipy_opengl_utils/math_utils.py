import numpy as np

def unproject_ray(ndc_x, ndc_y, camera):
    """
    Unprojects a ray from normalized device coordinates (NDC) to world space.
    Returns (ray_origin, ray_direction).
    """
    proj = np.asarray(camera.get_projection_matrix()).T  # Transpose here
    view = np.asarray(camera.get_view_matrix()).T        # Transpose here

    inv_vp = np.linalg.inv(proj @ view)

    near = np.array([ndc_x, ndc_y, -1, 1], dtype=np.float32)
    far  = np.array([ndc_x, ndc_y,  1, 1], dtype=np.float32)

    near_world = inv_vp @ near
    far_world = inv_vp @ far
    near_world /= near_world[3]
    far_world /= far_world[3]

    ray_origin = near_world[:3]
    ray_dir = far_world[:3] - near_world[:3]
    ray_dir /= np.linalg.norm(ray_dir)
    return ray_origin, ray_dir

def ray_sphere_intersect(ray_origin, ray_dir, sphere_center, sphere_radius):
    """
    Tests intersection between a ray and a sphere by solving the analytical geometry equations.
    """

    # Ray-sphere intersection test
    oc = ray_origin - sphere_center
    a = np.dot(ray_dir, ray_dir)
    b = 2.0 * np.dot(oc, ray_dir)
    c = np.dot(oc, oc) - sphere_radius * sphere_radius
    discriminant = b * b - 4 * a * c
    if discriminant < 0:
        return False, None
    dist = (-b - np.sqrt(discriminant)) / (2.0 * a)
    return dist > 0, dist

