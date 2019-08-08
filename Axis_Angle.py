#
# Quick Python program to find the angle and axis of rotation of a vector from initial state to final state
#

import numpy as np
import math
import argparse

parser = argparse.ArgumentParser(description='Find the single axis and angle of a vector after two rotations')
parser.add_argument('v0x', metavar='v0x', type=float, help='the intial vector to rotate, x component')
parser.add_argument('v0y', metavar='v0y', type=float, help='the intial vector to rotate, y component')
parser.add_argument('v0z', metavar='v0z', type=float, help='the intial vector to rotate, z component')
parser.add_argument('axis0x', metavar='axis0x', type=float, help='first axis of rotation, x component')
parser.add_argument('axis0y', metavar='axis0y', type=float, help='first axis of rotation, y component')
parser.add_argument('axis0z', metavar='axis0z', type=float, help='first axis of rotation, z component')
parser.add_argument('theta0', metavar='theta0', type=float, help='first angle of rotation in radians')
parser.add_argument('axis1x', metavar='axis1x', type=float, help='second axis of rotation, x component')
parser.add_argument('axis1y', metavar='axis1y', type=float, help='second axis of rotation, y component')
parser.add_argument('axis1z', metavar='axis1z', type=float, help='second axis of rotation, z component')
parser.add_argument('theta1', metavar='theta1', type=float, help='second angle of rotation in radians')
args = parser.parse_args()

def rotation_matrix(axis, theta):
     """
     Return the rotation matrix associated with counterclockwise rotation about
     the given axis by theta radians.
     """
     axis = np.asarray(axis)
     axis = axis / math.sqrt(np.dot(axis, axis))
     a = math.cos(theta / 2.0)
     b, c, d = -axis * math.sin(theta / 2.0)
     aa, bb, cc, dd = a * a, b * b, c * c, d * d
     bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
     return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                      [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                      [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])

def angle(v1, v2):
     return np.arccos(np.dot(v1, v2) / (np.linalg.norm(v1)*np.linalg.norm(v2)))
     
# rotation
def rot(axis0, theta0, v0):
	return np.dot(rotation_matrix(axis0, theta0), v0)

# magnitude
def mag(v0):
	return np.linalg.norm(v0)
	
# angle
def angle(v0, v1):
	return np.arccos( np.dot(v0, v1) / (mag(v0) * mag(v1)) )
	
"""
Use: 
	v0 = np.array([x, y, z])
	vf = rot(axis1, theta1, rot(axis0, theta0, v0) )
	axis = np.cross(v0, vf)
	theta = angle(v0, vf)
"""

# arg assignment
v0 = np.array([args.v0x, args.v0y, args.v0z])
axis0 = np.array([args.axis0x, args.axis0y, args.axis0z])
theta0 = args.theta0
axis1 = np.array([args.axis1x, args.axis1y, args.axis1z])
theta1 = args.theta1

vf = rot(axis1, theta1, rot(axis0, theta0, v0) )
axis = np.cross(v0, vf) / mag( np.cross(v0, vf) )
theta = angle(v0, vf)

# arg check
print("Arg check: ")
print("v0 = [ ", v0[0], ", ", v0[1], ", ", v0[2], " ]")
print("axis0 = [ ", axis0[0], ", ", axis0[1], ", ", axis0[2], " ]" )
print("theta0 = ", theta0)
print("axis1 = [ ", axis1[0], ", ", axis1[1], ", ", axis1[2], " ]" )
print("theta1 = ", theta1)

# result check
v1 = rot(axis0, theta0, v0)
print("v after 1 rotation = [ ", v1[0], ", ", v1[1], ", ", v1[2], " ]" )
print("vf = [ ", vf[0], ", ", vf[1], ", ", vf[2], " ]" )

print("axis = [ ", axis[0], ", ", axis[1], ", ", axis[2], " ]" )
print("angle = ", theta)

vf1 = rot(axis, theta, v0)
print("vf using new rot = ", vf1[0], ", ", vf1[1], ", ", vf1[2], " ]" )




