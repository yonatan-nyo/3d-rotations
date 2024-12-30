import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import time
import tracemalloc
from rotator import Rotator
from scipy.spatial.transform import Rotation as R
from tabulate import tabulate

# Define basis vectors for Geometric Algebra manually
e1 = np.array([1, 0, 0])
e2 = np.array([0, 1, 0])
e3 = np.array([0, 0, 1])


def euler_to_quaternion(roll, pitch, yaw, order='XYZ'):
    r = R.from_euler(order.lower(), [roll, pitch, yaw], degrees=True)
    return r.as_quat()


def euler_to_axis_angle(roll, pitch, yaw, order='XYZ'):
    r = R.from_euler(order.lower(), [roll, pitch, yaw], degrees=True)
    angle = np.linalg.norm(r.as_rotvec())
    axis = r.as_rotvec() / (angle if angle > 1e-6 else 1)
    return angle, axis


class Cube:
    def __init__(self, size=1):
        self.size = size
        self.vertices = self._create_cube()

    def _create_cube(self):
        s = self.size / 2
        return np.array([
            [s, s, s], [s, s, -s], [s, -s, s], [s, -s, -s],
            [-s, s, s], [-s, s, -s], [-s, -s, s], [-s, -s, -s]
        ])


class Plotter:
    @staticmethod
    def plot_cube(ax, vertices, color='b'):
        edges = [
            (0, 1), (1, 3), (3, 2), (2, 0),  # Top edges
            (4, 5), (5, 7), (7, 6), (6, 4),  # Bottom edges
            (0, 4), (1, 5), (2, 6), (3, 7)  # Vertical edges
        ]
        for edge in edges:
            points = vertices[np.array(edge)]
            ax.plot3D(*points.T, color)


class Visualizer:
    # Static properties to track total time, memory, and peak memory for each method
    total_time = {}
    total_memory = {}
    peak_memory = {}

    @staticmethod
    def benchmark_rotation(method, vertices, *args):
        tracemalloc.start()
        start_time = time.perf_counter()
        rotated_vertices = method(vertices, *args)
        end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        elapsed_time = end_time - start_time
        current_memory = current / 10**6
        peak_memory_usage = peak / 10**6

        # Store results in static properties
        method_name = method.__name__
        if method_name not in Visualizer.total_time:
            Visualizer.total_time[method_name] = 0
            Visualizer.total_memory[method_name] = 0
            Visualizer.peak_memory[method_name] = 0

        Visualizer.total_time[method_name] += elapsed_time
        Visualizer.total_memory[method_name] += current_memory
        Visualizer.peak_memory[method_name] = max(
            Visualizer.peak_memory[method_name], peak_memory_usage)

        return rotated_vertices

    @staticmethod
    def set_up_axes(ax, limits=(-2, 2)):
        ax.set_xlim([limits[0], limits[1]])
        ax.set_ylim([limits[0], limits[1]])
        ax.set_zlim([limits[0], limits[1]])
        ax.set_box_aspect([1, 1, 1])

    @staticmethod
    def visualize(cube, operations, rotation_methods=None):
        fig = plt.figure(figsize=(19, 7))
        gs = GridSpec(len(operations) + 1, len(rotation_methods) + 1, figure=fig,
                      height_ratios=[0.1] + [1] * len(operations))

        for j, method in enumerate(rotation_methods):
            ax = fig.add_subplot(gs[0, j + 1])
            ax.set_title(method, fontsize=10)
            ax.axis('off')

        for i, angles in enumerate(operations):
            ax = fig.add_subplot(gs[i + 1, 0])
            ax.set_title(f"Operation {i + 1}\n{angles}", fontsize=10)
            ax.axis('off')

        for i, angles in enumerate(operations):
            quaternion = euler_to_quaternion(*angles, order='XYZ')
            ga_angle, ga_axis = euler_to_axis_angle(*angles, order='XYZ')
            zyxAngle = [angles[2], angles[1], angles[0]]
            nonZeroIndexes = [
                i for i, angle in enumerate(angles) if angle != 0]

            for j, method in enumerate(rotation_methods):
                ax = fig.add_subplot(gs[i + 1, j + 1], projection='3d')
                Visualizer.set_up_axes(ax)

                if method == 'Euler':
                    # if there is >1 non-zero angle, use the euler
                    # else use euler_one_degree
                    if len(nonZeroIndexes) > 1:
                        rotated = Visualizer.benchmark_rotation(
                            Rotator.euler, cube.vertices, zyxAngle)
                    else:
                        rotated = Visualizer.benchmark_rotation(
                            Rotator.euler_one_degree, cube.vertices, angles[nonZeroIndexes[0]], 'XYZ'[nonZeroIndexes[0]])
                    color = 'r'
                elif method == 'Euler Manual':
                    rotated = Visualizer.benchmark_rotation(
                        Rotator.euler_manual_all_degree, cube.vertices, zyxAngle)
                    color = 'g'
                elif method == 'Matrix':
                    rotated = Visualizer.benchmark_rotation(
                        Rotator.matrix, cube.vertices, zyxAngle)
                    color = 'b'
                elif method == 'Quaternion':
                    rotated = Visualizer.benchmark_rotation(
                        Rotator.quaternion, cube.vertices, quaternion)
                    color = 'y'
                elif method == 'Rodrigues':
                    rotated = Visualizer.benchmark_rotation(
                        Rotator.rodrigues, cube.vertices, ga_axis, ga_angle)
                    color = 'c'
                else:
                    rotated = cube.vertices
                    color = 'k'

                Plotter.plot_cube(ax, rotated, color)

        plt.subplots_adjust(hspace=0.5, wspace=0.5)
        Visualizer.print_summary()
        plt.show()

    @staticmethod
    def print_summary():
        lowest_time = float('inf')
        lowest_time_method = ''
        lowest_memory = float('inf')
        lowest_memory_method = ''

        print("Summary of Rotation Methods:")
        data = []

        for method in Visualizer.total_time:
            if Visualizer.total_time[method] <= lowest_time:
                lowest_time = Visualizer.total_time[method]
                lowest_time_method = method
            if Visualizer.total_memory[method] <= lowest_memory:
                lowest_memory = Visualizer.total_memory[method]
                lowest_memory_method = method
            data.append([
                method,
                f"{Visualizer.total_time[method]:.6f}s",
                f"{Visualizer.total_memory[method]:.6f}MB",
                f"{Visualizer.peak_memory[method]:.6f}MB"
            ])

        headers = ["Method", "Total Time", "Total Memory", "Peak Memory"]
        print(tabulate(data, headers=headers, tablefmt="grid"))
        print(
            f"\n{lowest_time_method} has the lowest total time of {lowest_time:.6f}s")
        print(
            f"{lowest_memory_method} has the lowest total memory of {lowest_memory:.6f}MB")


if __name__ == "__main__":
    cube = Cube(size=3)

    # List of operations in degrees
    # operations = [
    #     [0, 90, 0],   # Pitch 90° (gimbal lock)
    #     [45, 10, 0],  # Pitch 90° with yaw 45°
    #     [30, -90, 10],  # Pitch -90° with yaw 30° and roll 10°
    #     [60, 90, 50]  # Pitch 90° with yaw 60° and roll 50°
    # ]

    # single axis rotation
    # operations = [[angle, 0, 0] for angle in range(10, 41, 10)]
    # operations = [[0, angle, 0] for angle in range(10, 41, 10)]
    # operations = [[0, 0, angle] for angle in range(10, 41, 10)]

    # two axis rotation
    # operations = [[angle, 0, angle] for angle in range(10, 41, 10)]
    # operations = [[0, angle, angle] for angle in range(10, 41, 10)]
    # operations = [[angle, angle, 0] for angle in range(10, 41, 10)]

    # three axis rotation
    operations = [[angle, angle, angle] for angle in range(10, 41, 10)]

    # Define methods to visualize, you can modify this list
    rotation_methods = [
        'Euler',
        'Euler Manual',
        'Matrix',
        'Quaternion',
        'Rodrigues',
    ]

    print("\nrotations: ", operations)

    # Visualize the selected methods
    Visualizer.visualize(cube, operations, rotation_methods)
