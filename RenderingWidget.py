from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtGui import QMouseEvent, QWheelEvent
from OpenGL.GL import *
import numpy as np

class RenderingWidget(QOpenGLWidget):
    """
    이 위젯은 model을 GL 화면에 렌더링한다.
    마우스 입력을 받아 모델의 rotation, scale 등 Model Matrix를 조정한다.

    Attributes:
        mesh (TriangleMesh): Rendering 될 model
        mouse_latest(NDArray): 직전의 마우스 위치. [0]=x, [1]=y
        rotation(NDArray): model에 적용될 3D rotation matrix (4 x 4)
        scale(float): model에 적용될 scale 배율. 확대(>1), 축소(<1)

    Methods:
        set_mesh: model을 설정하고 화면을 다시 그린다
    """

    mesh = None
    mouse_latest = None
    rotation = np.identity(4)
    scale = 1.0

    def __init__(self):
        super().__init__()

    def set_mesh(self, mesh):
        """
        렌더링할 model을 설정하고 다시 그린다

        Args:
            mesh (TriangleMesh): model의 mesh object
        """
        self.mesh = mesh
        self.update()

    def initializeGL(self) -> None:
        """
        GL의 상태머신, 조명을 초기화한다
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

        glViewport(0, 0, width, height)

        # Perspective
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width / height, 0.1, 1000)

        # Camera
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(0, 0, 200, 0, 0, 0, 0, 1, 0)

    def setup_lighting(self):
        """
        model의 음영, 질감 표현을 위해 조명, material을 설정한다.
        """
        light_position = [0.0, 50.0, 150.0, 0.0]
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 100.0)

    def paintGL(self):
        """
        model을 rendering한다.
        """
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()

        mesh = self.mesh
        if mesh is not None:
            # 모델을 원점으로 옮기고 scale 및 rotation을 적용한다.
            center = mesh.get_center()
            glMultMatrixf(self.rotation)
            glScalef(self.scale, self.scale, self.scale)
            glTranslatef(-center[0], -center[1], -center[2])

            # mesh의 polygon을 모두 그린다 (gray)
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
        (performance를 위해 inverse projection 사용하지 않는다.)
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
        휠 사용 시 모델의 scale 배율 적용 후 다시 렌더링.
        """
        if a0.angleDelta().y() > 0:
            self.scale *= 1.2
        else:
            self.scale *= 0.8
        self.update()
        return super().wheelEvent(a0)
    
    def apply_matrix(self, original, applied):
        """
        기존 변환에 새로운 변환을 가한다. 

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
        axis를 축으로 angle(in degree)만큼 회전시키는 행렬 계산

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