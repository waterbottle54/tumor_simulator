import numpy as np
import open3d as o3d

def reconstruct_surface(points):
    
    # build mesh object
    points = np.array(points)
    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(points)
    
    point_cloud.estimate_normals()
    # a call to orient_normals_towards_camera_location() invokes runtime crash for unknown reason. what I have tried:
    # removing point_cloud.get_center(), version adjustment(both python and open3d), data inspection(points)
    # As a workaround, I chose to adjust lighting in openGL part (in RenderingWidget.py) - 2024.11
    #point_cloud.orient_normals_towards_camera_location(point_cloud.get_center()) <= INVOKES CRASH
    point_cloud.normals = o3d.utility.Vector3dVector( - np.asarray(point_cloud.normals))

    mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(point_cloud, depth=7, width=0, scale=1.1, linear_fit=False)[0]
    mesh = mesh.simplify_quadric_decimation(1000)

    mesh.remove_degenerate_triangles()
    mesh.remove_duplicated_triangles()
    mesh.remove_duplicated_vertices()
    mesh.remove_non_manifold_edges()

    bbox = point_cloud.get_axis_aligned_bounding_box()
    mesh = mesh.crop(bbox)

    mesh.compute_vertex_normals()
    mesh.compute_triangle_normals()

    return mesh