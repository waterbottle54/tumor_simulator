from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtGui import QMouseEvent, QWheelEvent
from OpenGL.GL import *
import numpy as np

class RenderingWidget(QOpenGLWidget):
    """
    입력받은 mesh를 렌더링하는 위젯.
    - OpenGL perspective projection을 적용한다.
    - 드래그를 인식해 mesh의 회전, scale을 조정한다.

    Attributes:
        mesh (TriangleMesh):    렌더링할 mesh
        mouse_latest(NDArray):  드래그 마지막 위치.(x=[0], y=[1])
        rotation(NDArray):      mesh 적용될 3D rotation matrix (4 x 4)
        scale(float):           mesh 적용될 scale 배율. 확대(>1), 축소(<1)

    Methods:
        set_mesh: 렌더링할 mesh를 설정하고 화면을 다시 그린다.
        initializeGL: OpenGL의 state machine 및 lighting을 초기화한다.
        resizeGL: 요청된 크기로 viewport를 조정한다.
        setup_lighting: mesh의 음영 표현을 위해 조명을 설정한다.
        paintGL: mesh를 렌더링한다.
        mousePressEvent: 마우스 press 위치를 저장하고 drag 인식을 시작한다.
        mouseReleaseEvent: 마우스가 release 되면 drag 인식을 끝낸다.
        mouseMoveEvent: 마우스 drag를 인식하여 모델의 rotation을 변경한다.
        wheelEvent: 마우스 휠 회전 시 모델의 scale 배율 적용 후 다시 렌더링한다.
        apply_matrix: mesh에 적용되는 기존 변환에 추가 변환을 적용한다.
        get_rotation_matrix: axis를 축으로 angle(in degrees)만큼 회전시키는 행렬을 계산한다.
    """

    # Copyright (c) 2023 Sung Won Jo
    # For more details: https://github.com/waterbottle54/tumor_simulator

    def __init__(self):
        super().__init__()
        self.mesh = None
        self.mouse_latest = None
        self.rotation = np.identity(4)
        self.scale = 1.0

    def set_mesh(self, mesh):
        """
        렌더링할 mesh를 설정하고 화면을 업데이트한다

        Args:
            mesh (TriangleMesh): mesh object to be rendered
        """
        self.mesh = mesh
        self.update()

    def initializeGL(self) -> None:
        """
        OpenGL의 state machine 및 lighting을 초기화한다
        """

        glClearColor(0.0, 0.0, 0.0, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        self.setup_lighting()

    def resizeGL(self, width, height):
        """
        요청된 크기로 viewport를 조정한다

        Args:
            width (int): 요청된 viewport 폭
            height (int): 요청된 viewport 높이
        """
        from OpenGL.GLU import gluPerspective, gluLookAt

        # set viewport matrix
        glViewport(0, 0, width, height)

        # set perspective projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width / height, 0.1, 1000)

        # setup camera
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(0, 0, 200, 0, 0, 0, 0, 1, 0)

    def setup_lighting(self):
        """
        mesh model의 음영, 질감 표현을 위해 조명, material을 설정한다.
        """
        light_position = [0.0, 50.0, 150.0, 0.0]
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 100.0)

    def paintGL(self):
        """
        mesh를 렌더링한다.
        """
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()

        mesh = self.mesh
        if mesh is not None:
            # mesh model을 원점으로 옮기고 scale 및 rotation을 적용한다.
            center = mesh.get_center()
            glMultMatrixf(self.rotation)
            glScalef(self.scale, self.scale, self.scale)
            glTranslatef(-center[0], -center[1], -center[2])

            # mesh의 polygon을 모두 그린다 (gray color)
            vertices = np.asarray(mesh.vertices)
            normals = np.asarray(mesh.vertex_normals)
            glBegin(GL_TRIANGLES)
            glColor3ub(192, 192, 192)
            for i in range(len(mesh.triangles)):
                triangle = mesh.triangles[i]
                for j in range(3):
                    vertex_idx = triangle[j]
                    normal = normals[vertex_idx]
                    vertex = vertices[vertex_idx]
                    glNormal3f(*normal)
                    glVertex3f(*vertex)
            glEnd()

        glPopMatrix()

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        """
        마우스 press 위치를 저장하고 drag 인식을 시작한다
        """
        self.mouse_latest = np.array([ float(a0.pos().x()), float(a0.pos().y()) ])
        return super().mousePressEvent(a0)
    
    def mouseReleaseEvent(self, a0: QMouseEvent) -> None:
        """
        release 되면 drag 인식을 끝낸다
        """
        self.mouse_latest = None
        return super().mouseReleaseEvent(a0)
    
    def mouseMoveEvent(self, a0: QMouseEvent) -> None:
        """
        마우스 drag를 인식하여 모델의 rotation을 변경한다.
        model에서 가까운 영역을 drag하면 (x,y,0)-axis rotation을 적용하고,
        model에서 먼 영역을 drag하면 z-axis rotation을 적용한다.
        (performance를 위해 inverse projection 미사용)
        """
        if self.mouse_latest is not None: # drag 중일 때
            new_rotation = None
            center = np.array([ self.width()/2.0, self.height()/2.0 ])
            mouse = np.array([ a0.pos().x(), a0.pos().y() ], dtype=np.float64)
            r = mouse - center  # r: viewport 중심점 기준 mouse의 상대좌표
            if np.linalg.norm(r) >= 100: 
                # drag가 model에서 멀 때 z-axis 회전 계산
                r_prev = self.mouse_latest - center
                angle = (np.linalg.norm(r - r_prev) / np.linalg.norm(r)) * (180 / np.pi)
                axis = np.cross(np.append(r, 0), np.append(r_prev, 0))  # cross of two vectors on xy-plane -> z-axis
                norm = np.linalg.norm(axis)
                if norm > 0:
                    axis /= norm
                    new_rotation = self.get_rotation_matrix(axis, angle)
            else:
                # drag가 model에 가까울 때, (x,y,0)-axis 회전 계산
                diff = mouse - self.mouse_latest
                axis = np.append(diff[::-1], 0)  # (x,y,0) rotation
                norm = np.linalg.norm(axis)
                axis /= norm
                angle = norm / 100 * 90
                new_rotation = self.get_rotation_matrix(axis, angle)
            if new_rotation is not None:
                # 산출된 미소 회전을 기존 회전 변환에 적용 후 다시 렌더링.
                self.rotation = self.apply_matrix(self.rotation, new_rotation)
                self.update()
        self.mouse_latest = mouse
        return super().mouseMoveEvent(a0)
    
    def wheelEvent(self, a0: QWheelEvent) -> None:
        """
        마우스 휠 회전 시 모델의 scale 배율 적용 후 다시 렌더링한다.
        """
        if a0.angleDelta().y() > 0:
            self.scale *= 1.2
        else:
            self.scale *= 0.8
        self.update()
        return super().wheelEvent(a0)
    
    def apply_matrix(self, original, applied):
        """
        mesh에 적용되는 기존 변환에 추가 변환을 적용한다.

        Args:
            original (NDArray): 기존 변환을 나타내는 행령
            applied (NDArray): 기존 변환에 적용될 미소 변환

        Returns:
            NDArray: 미소 변환이 적용된 새로운 행렬
        """
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadMatrixf(applied)
        glMultMatrixf(original)
        new = glGetFloatv(GL_MODELVIEW_MATRIX)
        glPopMatrix()
        return new

    def get_rotation_matrix(self, axis, angle):
        """
        axis를 축으로 angle(in degrees)만큼 회전시키는 행렬 계산

        Args:
            axis (NDArray): 축 벡터 (x, y, z) 
            angle (float): 회전각 (0~360)

        Returns:
            NDArray: 계산된 행렬
        """
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glRotatef(angle, axis[0], axis[1], axis[2])
        rot = glGetFloatv(GL_MODELVIEW_MATRIX)
        glPopMatrix()
        return rot