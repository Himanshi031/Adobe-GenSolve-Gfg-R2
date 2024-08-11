import numpy as np
from svgpathtools import svg2paths, Line, CubicBezier, Path
import matplotlib.pyplot as plt

def svg_to_segments(svg_path):
    paths, _ = svg2paths(svg_path)
    arr = []
    for path in paths:
        for segment in path:
            if isinstance(segment, (Line, CubicBezier)):
                arr.append(segment)
    print(f"Total segments extracted: {len(arr)}")
    return arr

def is_outer_square(segment, all_segments):
    start, end = segment.start, segment.end
    max_distance = max(abs(start.real), abs(start.imag), abs(end.real), abs(end.imag))
    return max_distance > 0.9 * max(max(abs(s.start.real), abs(s.start.imag), abs(s.end.real), abs(s.end.imag)) for s in all_segments)

def create_perfect_square(segments):
    points = np.array([(s.start.real, s.start.imag) for s in segments] +
                      [(s.end.real, s.end.imag) for s in segments])
    min_x, min_y = np.min(points, axis=0)
    max_x, max_y = np.max(points, axis=0)
    side = max(max_x - min_x, max_y - min_y)
    center_x, center_y = (min_x + max_x) / 2, (min_y + max_y) / 2
    half_side = side / 2
    square_points = [
        complex(center_x - half_side, center_y - half_side),
        complex(center_x + half_side, center_y - half_side),
        complex(center_x + half_side, center_y + half_side),
        complex(center_x - half_side, center_y + half_side)
    ]
    return [Line(square_points[i], square_points[(i+1)%4]) for i in range(4)]

def regularize_segments(segments):
    outer_segments = [s for s in segments if is_outer_square(s, segments)]
    inner_segments = [s for s in segments if s not in outer_segments]
    
    print(f"Outer segments: {len(outer_segments)}")
    print(f"Inner segments: {len(inner_segments)}")
    
    regularized_segments = create_perfect_square(outer_segments)
    regularized_segments.extend(inner_segments)
    
    return regularized_segments

def plot_segments(segments):
    fig, ax = plt.subplots(figsize=(6, 6))
    for segment in segments:
        if isinstance(segment, Line):
            points = np.array([segment.start, segment.end])
        elif isinstance(segment, CubicBezier):
            t = np.linspace(0, 1, 100)
            points = np.array([segment.point(ti) for ti in t])
        ax.plot(points.real, points.imag, 'k-', linewidth=2)
    ax.set_aspect('equal')
    ax.axis('off')
    plt.tight_layout()
    plt.show()

def save_segments_to_svg(segments, svg_path, size):
    import svgwrite
    dwg = svgwrite.Drawing(svg_path, size=(size, size))
    for segment in segments:
        if isinstance(segment, Line):
            dwg.add(dwg.line(start=(segment.start.real, segment.start.imag),
                             end=(segment.end.real, segment.end.imag),
                             stroke='black', stroke_width=2))
        elif isinstance(segment, CubicBezier):
            path = dwg.path(d=f'M {segment.start.real},{segment.start.imag} '
                            f'C {segment.control1.real},{segment.control1.imag} '
                            f'{segment.control2.real},{segment.control2.imag} '
                            f'{segment.end.real},{segment.end.imag}',
                            stroke='black', fill='none', stroke_width=2)
            dwg.add(path)
    dwg.save()

if __name__ == "__main__":
    input_svg = "data/problems/frag0.svg" # add your path to the input file
    output_svg = "regularized_output.svg"
    
    try:
        segments = svg_to_segments(input_svg)
        regularized_segments = regularize_segments(segments)
        
        if regularized_segments:
            plot_segments(regularized_segments)
            save_segments_to_svg(regularized_segments, output_svg, 100)
            print(f"Regularized SVG saved to {output_svg}")
        else:
            print("No valid segments found in the input SVG.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
