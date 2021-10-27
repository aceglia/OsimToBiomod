import inspect
import numpy as np


def index_go_to(_root, _tag, _attrib='False', _attribvalue='', index=''):
    # return index to go to _tag which can have condition on its attribute
    i = 0
    for _child in _root:
        if type(_child) == str:
            return ''
        if _attrib != 'False':
            if _child.tag == _tag and _child.get(_attrib) == _attribvalue:
                return index + '[{}]'.format(i)
            else:
                i += 1
        else:
            if _child.tag == _tag:
                return index + '[{}]'.format(i)
            else:
                i += 1
                # not found in children, go to grand children
    else:
        j = 0
        if _root is not None:
            for _child in _root:
                a = index_go_to(_child, _tag, _attrib, _attribvalue, index + '[{}]'.format(j))
                if a:
                    return a
                else:
                    j += 1
            else:
                return None

def go_to(_root, _tag, _attrib='False', _attribvalue=''):
    # return element corresponding to _tag
    # which can have condition on its attribute
    _index = index_go_to(_root, _tag, _attrib, _attribvalue)
    if _index is None:
        return 'None'
    else:
        _index = index_go_to(_root, _tag, _attrib, _attribvalue)
        return eval(retrieve_name(_root) + _index)

def retrieve_name(var):
    """
    Gets the name of var. Does it from the out most frame inner-wards.
    :param var: variable to get name from.
    :return: string
    """
    for fi in reversed(inspect.stack()):
        names = [var_name for var_name, var_val in fi.frame.f_locals.items() if var_val is var]
        if len(names) > 0:
            return names[0]

def new_text(element):
    if type(element) == str:
        return element
    else:
        return element.text

def compute_matrix_rotation(_rot_value):
    rot_x = np.array([[1, 0, 0],
                      [0, np.cos(_rot_value[0]), - np.sin(_rot_value[0])],
                      [0, np.sin(_rot_value[0]), np.cos(_rot_value[0])]])

    rot_y = np.array([[np.cos(_rot_value[1]), 0, np.sin(_rot_value[1])],
                      [0, 1, 0],
                      [-np.sin(_rot_value[1]), 0, np.cos(_rot_value[1])]])

    rot_z = np.array([[np.cos(_rot_value[2]), - np.sin(_rot_value[2]), 0],
                      [np.sin(_rot_value[2]), np.cos(_rot_value[2]), 0],
                      [0, 0, 1]])
    rot_matrix = np.dot(rot_z, np.dot(rot_y, rot_x))
    return rot_matrix

def rot2eul(R):
    beta = -np.arcsin(R[2,0])
    alpha = np.arctan2(R[2,1],R[2,2])
    gamma = np.arctan2(R[1,0],R[0,0])
    return np.array((alpha, beta, gamma))

def coord_sys(axis):
    # define orthonormal coordinate system with given z-axis
    [a, b, c] = axis
    if a == 0:
        if b == 0:
            if c == 0:
                return [[1, 0, 0], [0, 1, 0], [0, 0, 1]], ''
            else:
                return [[1, 0, 0], [0, 1, 0], [0, 0, 1]], 'z'
        else:
            if c == 0:
                return [[1, 0, 0], [0, 1, 0], [0, 0, 1]], 'y'
            else:
                y_temp = [0, -c / b, 1]
    else:
        if b == 0:
            if c == 0:
                return [[1, 0, 0], [0, 1, 0], [0, 0, 1]], 'x'
            else:
                y_temp = [-c / a, 0, 1]
        else:
            y_temp = [-b / a, 1, 0]
    z_temp = [a, b, c]
    x_temp = np.cross(y_temp, z_temp)
    norm_x_temp = np.linalg.norm(x_temp)
    norm_z_temp = np.linalg.norm(z_temp)
    x = [1 / norm_x_temp * x_el for x_el in x_temp]
    z = [1 / norm_z_temp * z_el for z_el in z_temp]
    y = [y_el for y_el in np.cross(z, x)]
    return [x, y, z], ''


def ortho_norm_basis(vector, idx):
    # build an orthogonal basis fom a vector
    basis = []
    v = np.random.random(3)
    z = np.cross(v, vector)
    z_norm = z / np.linalg.norm(z)
    y = np.cross(vector, z)
    y_norm = y / np.linalg.norm(y)
    if idx == 0:
        basis = np.append(vector, np.append(y_norm, z_norm)).reshape(3, 3).T
        if np.linalg.det(basis) < 0:
            basis = np.append(vector, np.append(y_norm, -z_norm)).reshape(3, 3).T
    elif idx == 1:
        basis = np.append(y_norm, np.append(vector, z_norm)).reshape(3, 3).T
        if np.linalg.det(basis) < 0:
            basis = np.append(y_norm, np.append(vector, -z_norm)).reshape(3, 3).T
    elif idx == 2:
        basis = np.append(z_norm, np.append(y_norm, vector)).reshape(3, 3).T
        if np.linalg.det(basis) < 0:
            basis = np.append(-z_norm, np.append(y_norm, vector)).reshape(3, 3).T
    return basis


def is_ortho_basis(basis):
    return False if np.dot(basis[0], basis[1]) != 0 or np.dot(basis[1], basis[2]) != 0 or np.dot(basis[0], basis[2]) != 0 else True


class OrthoMatrix:
    def __init__(self, translation=[0, 0, 0], rotation_1=[0, 0, 0], rotation_2=[0, 0, 0], rotation_3=[0, 0, 0]):
        self.trans = np.transpose(np.array([translation]))
        self.axe_1 = rotation_1  # axis of rotation for theta_1
        self.axe_2 = rotation_2  # axis of rotation for theta_2
        self.axe_3 = rotation_3  # axis of rotation for theta_3
        self.rot_1 = np.transpose(np.array(coord_sys(self.axe_1)[0]))  # rotation matrix for theta_1
        self.rot_2 = np.transpose(np.array(coord_sys(self.axe_2)[0]))  # rotation matrix for theta_2
        self.rot_3 = np.transpose(np.array(coord_sys(self.axe_3)[0]))  # rotation matrix for theta_3
        self.rotation_matrix = self.rot_3.dot(self.rot_2.dot(self.rot_1))  # rotation matrix for
        self.matrix = np.append(np.append(self.rotation_matrix, self.trans, axis=1), np.array([[0, 0, 0, 1]]), axis=0)

    def get_rotation_matrix(self):
        return self.rotation_matrix

    def set_rotation_matrix(self, rotation_matrix):
        self.rotation_matrix = rotation_matrix

    def get_translation(self):
        return self.trans

    def set_translation(self, trans):
        self.trans = trans

    def get_matrix(self):
        self.matrix = np.append(np.append(self.rotation_matrix, self.trans, axis=1), np.array([[0, 0, 0, 1]]), axis=0)
        return self.matrix

    def transpose(self):
        self.rotation_matrix = np.transpose(self.rotation_matrix)
        self.trans = -self.rotation_matrix.dot(self.trans)
        self.matrix = np.append(np.append(self.rotation_matrix, self.trans, axis=1), np.array([[0, 0, 0, 1]]), axis=0)
        return self.matrix

    def product(self, other):
        self.rotation_matrix = self.rotation_matrix.dot(other.get_rotation_matrix())
        self.trans = self.trans + other.get_translation()
        self.matrix = np.append(np.append(self.rotation_matrix, self.trans, axis=1), np.array([[0, 0, 0, 1]]), axis=0)

    def get_axis(self):
        return coord_sys(self.axe_1)[1] + coord_sys(self.axe_2)[1] + coord_sys(self.axe_3)[1]

def out_product(rotomatrix_1, rotomatrix_2):
    rotomatrix_prod = OrthoMatrix()
    rotomatrix_prod.set_translation(rotomatrix_1.get_translation() + rotomatrix_2.get_translation())
    rotomatrix_prod.set_rotation_matrix(rotomatrix_1.get_rotation_matrix().dot(rotomatrix_2.get_rotation_matrix()))
    rotomatrix_prod.get_matrix()
    return rotomatrix_prod