import open3d as o3d
import numpy as np

def reconstruct_surface(points):

    # build mesh object
    points = np.array(points)
    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(points)
    point_cloud.estimate_normals()

    point_cloud.orient_normals_towards_camera_location(point_cloud.get_center())
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