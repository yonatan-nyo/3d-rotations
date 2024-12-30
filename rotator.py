import numpy as np
from scipy.spatial.transform import Rotation as R
from typing import Literal


class Rotator:
    @staticmethod
    def euler_one_degree(vertices, angles, degree: Literal['X', 'Y', 'Z']):
        if (degree == 'X'):
            rx = np.array([
                [1, 0, 0],
                [0, np.cos(np.radians(angles)), -np.sin(np.radians(angles))],
                [0, np.sin(np.radians(angles)), np.cos(np.radians(angles))]
            ])
            return np.dot(vertices, rx.T)
        elif (degree == 'Y'):
            ry = np.array([
                [np.cos(np.radians(angles)), 0, np.sin(np.radians(angles))],
                [0, 1, 0],
                [-np.sin(np.radians(angles)), 0, np.cos(np.radians(angles))]
            ])
            return np.dot(vertices, ry.T)
        elif (degree == 'Z'):
            rz = np.array([
                [np.cos(np.radians(angles)), -np.sin(np.radians(angles)), 0],
                [np.sin(np.radians(angles)), np.cos(np.radians(angles)), 0],
                [0, 0, 1]
            ])
            return np.dot(vertices, rz.T)
        else:
            return vertices

    @staticmethod
    def euler(vertices, angles, order='ZYX'):
        # Convert angles to radians if they are in degrees
        r = R.from_euler(order, angles, degrees=True)
        return r.apply(vertices)

    @staticmethod
    def euler_manual_all_degree(vertices, angles, order='ZYX'):
        angles = np.radians(angles)
        cz = np.cos(angles[0])
        sz = np.sin(angles[0])
        cy = np.cos(angles[1])
        sy = np.sin(angles[1])
        cx = np.cos(angles[2])
        sx = np.sin(angles[2])

        rz = np.array([
            [cz, -sz, 0],
            [sz, cz, 0],
            [0, 0, 1]
        ])

        ry = np.array([
            [cy, 0, sy],
            [0, 1, 0],
            [-sy, 0, cy]
        ])

        rx = np.array([
            [1, 0, 0],
            [0, cx, -sx],
            [0, sx, cx]
        ])

        vertices = np.dot(vertices, rx.T)
        vertices = np.dot(vertices, ry.T)
        vertices = np.dot(vertices, rz.T)

        return vertices

    # other methods

    @staticmethod
    def matrix(vertices, angles):
        # Convert angles to radians
        angles = np.radians(angles)

        # Create rotation matrices for each axis
        ry = np.array([
            [np.cos(angles[1]), 0, np.sin(angles[1])],
            [0, 1, 0],
            [-np.sin(angles[1]), 0, np.cos(angles[1])]
        ])

        rz = np.array([
            [np.cos(angles[0]), -np.sin(angles[0]), 0],
            [np.sin(angles[0]), np.cos(angles[0]), 0],
            [0, 0, 1]
        ])

        rx = np.array([
            [1, 0, 0],
            [0, np.cos(angles[2]), -np.sin(angles[2])],
            [0, np.sin(angles[2]), np.cos(angles[2])]
        ])

        # Compute combined rotation matrix
        rotation_matrix = rz @ ry @ rx

        return np.dot(vertices, rotation_matrix.T)

    @staticmethod
    def quaternion(vertices, quaternion):
        # Normalize the quaternion to ensure a valid rotation
        quaternion = np.array(quaternion)
        if np.linalg.norm(quaternion) != 1:
            quaternion = quaternion / np.linalg.norm(quaternion)
        rotation = R.from_quat(quaternion)
        return rotation.apply(vertices)

    @staticmethod
    def rodrigues(vertices, axis, angle):
        # Normalize the axis of rotation
        axis = axis / np.linalg.norm(axis)
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)
        dot = np.dot(vertices, axis)
        cross = np.cross(axis, vertices)
        # Apply Rodrigues' rotation formula to each vertex
        return vertices * cos_a + cross * sin_a + axis * dot[:, None] * (1 - cos_a)
