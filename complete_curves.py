import numpy as np
import matplotlib.pyplot as plt
from svgpathtools import svg2paths2, Path
from shapely.geometry import LineString, Point, MultiLineString
from shapely.ops import linemerge, unary_union
from scipy.spatial import cKDTree

def svg_to_paths(svg_file):
    paths, _, _ = svg2paths2(svg_file)
    return paths

def path_to_line(path, num_points=100):
    t = np.linspace(0, 1, num_points)
    points = np.array([path.point(ti) for ti in t])
    return LineString([(float(p.real), float(p.imag)) for p in points])

def complete_curves(paths, max_distance=5):
    lines = [path_to_line(path) for path in paths]
    
    # Extract all endpoints
    endpoints = []
    for line in lines:
        endpoints.extend([Point(line.coords[0]), Point(line.coords[-1])])
    
    # Build KD-tree for efficient nearest neighbor search
    tree = cKDTree([(p.x, p.y) for p in endpoints])
    
    connections = []
    for i, p in enumerate(endpoints):
        distances, indices = tree.query((p.x, p.y), k=2)  # Find the nearest point (excluding self)
        nearest_index = indices[1]
        nearest_distance = distances[1]
        
        if nearest_distance <= max_distance:
            nearest_point = endpoints[nearest_index]
            connection = LineString([p, nearest_point])
            if not any(existing_line.crosses(connection) for existing_line in lines):
                connections.append(connection)
    
    # Merge original lines and new connections
    all_lines = lines + connections
    merged = linemerge(all_lines)
    
    # Ensure merged is always a list of LineStrings
    if isinstance(merged, LineString):
        merged = [merged]
    elif isinstance(merged, MultiLineString):
        merged = list(merged.geoms)
    
    # Final step: close any nearly closed curves
    final_curves = []
    for curve in merged:
        if not curve.is_ring:
            start, end = Point(curve.coords[0]), Point(curve.coords[-1])
            if start.distance(end) <= max_distance:
                curve = LineString(list(curve.coords) + [curve.coords[0]])
        final_curves.append(curve)
    
    return final_curves

svg_file_path = "data/problems/occlusion2_rec.svg"
paths = svg_to_paths(svg_file_path)
completed_curves = complete_curves(paths, max_distance=10)

plt.figure(figsize=(10, 10))

# Plot original curves
for path in paths:
    line = path_to_line(path)
    x, y = line.xy
    plt.plot(x, y, color='blue', linewidth=1, alpha=0.5)

# Plot completed curves
for curve in completed_curves:
    x, y = curve.xy
    plt.plot(x, y, color='red', linewidth=2)

plt.axis('equal')
plt.title("Completed Curves")
plt.savefig("completed_curves.png")
plt.show()

print(f"Number of original paths: {len(paths)}")
print(f"Number of completed curves: {len(completed_curves)}")
