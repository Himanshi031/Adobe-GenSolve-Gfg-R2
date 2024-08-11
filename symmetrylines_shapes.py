import numpy as np
import matplotlib.pyplot as plt
from svgpathtools import svg2paths2

def reflect_points_across_vertical(points, x_line):
    return np.array([[2 * x_line - x, y] for x, y in points])

def reflect_points_across_horizontal(points, y_line):
    return np.array([[x, 2 * y_line - y] for x, y in points])

def reflect_points_across_line(points, line_point, line_direction):
    line_point = np.array(line_point)
    line_direction = np.array(line_direction) / np.linalg.norm(line_direction)
    reflected_points = []
    for point in points:
        point = np.array(point)
        projection_length = np.dot(point - line_point, line_direction)
        projection = line_point + projection_length * line_direction
        reflection = 2 * projection - point
        reflected_points.append(reflection)
    return np.array(reflected_points)

def find_symmetry_and_reflect(path_XYs, symmetry_type):
    reflected_paths = []
    for path in path_XYs:
        reflected_path = []
        for segment in path:
            if symmetry_type == "vertical":
                x_line = (segment[:, 0].min() + segment[:, 0].max()) / 2
                reflected_segment = reflect_points_across_vertical(segment, x_line)
            elif symmetry_type == "horizontal":
                y_line = (segment[:, 1].min() + segment[:, 1].max()) / 2
                reflected_segment = reflect_points_across_horizontal(segment, y_line)
            elif symmetry_type == "diagonal":
                line_point = [(segment[:, 0].min() + segment[:, 0].max()) / 2,
                              (segment[:, 1].min() + segment[:, 1].max()) / 2]
                line_direction = [1, 1]  # 45-degree line
                reflected_segment = reflect_points_across_line(segment, line_point, line_direction)
            reflected_path.append(reflected_segment)
        reflected_paths.append(reflected_path)
    return reflected_paths

def plot_paths_with_symmetry(original_paths, reflected_paths, colours, symmetry_type, output_file):
    fig, ax = plt.subplots(figsize=(8, 8))
    color_idx = 0
    for original_path, reflected_path in zip(original_paths, reflected_paths):
        for segment, reflected_segment in zip(original_path, reflected_path):
            if len(segment) > 0:
                segment = np.array(segment)
                ax.plot(segment[:, 0], segment[:, 1], c=colours[color_idx % len(colours)], linewidth=2)
                ax.plot(reflected_segment[:, 0], reflected_segment[:, 1], c=colours[(color_idx + 1) % len(colours)], linestyle='--', linewidth=2)
        color_idx += 1
    ax.set_aspect('equal')
    plt.xlim(0, 150)
    plt.ylim(0, 150)
    plt.grid(True, which='both', color='lightgray', linestyle='--')
    plt.title(f"Original and {symmetry_type.capitalize()} Reflected Paths")
    plt.savefig(output_file)
    plt.show()

def read_svg(svg_path):
    paths, attributes, svg_attributes = svg2paths2(svg_path)
    path_XYs = []
    for path in paths:
        path_points = []
        for segment in path:
            segment_points = np.array([[point.real, point.imag] for point in segment])
            path_points.append(segment_points)
        path_XYs.append(path_points)
    return path_XYs

# Example usage
input_svg = 'data/problems/frag2.svg'
output_png_vertical = 'output_vertical.png'
output_png_horizontal = 'output_horizontal.png'
output_png_diagonal = 'output_diagonal.png'
colours = ['r', 'g', 'b']

# Read paths from SVG
simplified_paths = read_svg(input_svg)

# Debug: Print the paths read from the SVG
print("Original Paths:")
for path in simplified_paths:
    for segment in path:
        print(segment)

# Find and plot symmetry for vertical reflection
reflected_paths_vertical = find_symmetry_and_reflect(simplified_paths, "vertical")
plot_paths_with_symmetry(simplified_paths, reflected_paths_vertical, colours, "vertical", output_png_vertical)

# Find and plot symmetry for horizontal reflection
reflected_paths_horizontal = find_symmetry_and_reflect(simplified_paths, "horizontal")
plot_paths_with_symmetry(simplified_paths, reflected_paths_horizontal, colours, "horizontal", output_png_horizontal)

# Find and plot symmetry for diagonal reflection
reflected_paths_diagonal = find_symmetry_and_reflect(simplified_paths, "diagonal")
plot_paths_with_symmetry(simplified_paths, reflected_paths_diagonal, colours, "diagonal", output_png_diagonal)
