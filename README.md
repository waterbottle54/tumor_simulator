# 뇌종양 분석기 (Brain Tumor Simulator)
<p align="right">Copyright © 2023 조성원(Sung Won Jo)</p>

 ## Introduction

 Tumor Detection & 3D Modeling | Growth Pattern Analysis
:-----------------------------:|:------------------------:
![](https://github.com/waterbottle54/tumor_simulator/blob/main/screenshots/demo-model.png) | ![](https://github.com/waterbottle54/tumor_simulator/blob/main/screenshots/demo-graph.png)
 
 * **Brain Tumor Simulator**는 **Qt5 / Python** 으로 작성된 **Desktop** 의료 영상 소프트웨어입니다.<br>

   이 프로그램은 **DICOM** 데이터로부터 종양을 나타내는 3D 모델을 생성하고, 종양의 체적을 계산합니다.<br>

 * 이 프로그램은 의료 진단을 대체하는 용도로 사용될 수 없습니다.

   This application is not intended to replace professional medical diagnosis.

 ## Getting Started
> ### Dependencies
> * Windows: **10, 11**
> * python >= **3.0.9**
> 

> ### Installation
> * **Choice 1**. Repository의 **Main.py**를 python 인터프리터(>=3.0.9)로 실행합니다.
>   
>     *(Consts.py 모듈의 debug_or_release 를 True 로 설정합니다.)*
>   
> * **Choice 2**: 다음 링크에서 **실행파일**(.exe)을 다운로드 합니다.
>   
>     [[EXE] Brain Tumor Simulator.zip](https://drive.google.com/file/d/1jTMRluP4cpLhTS-4g9lGYfiC0SxKQW2w/view?usp=sharing)

 ## Funtionality
> ### Viewing
> * MRI 및 CT 영상이 담긴 DICOM 파일을 열람할 수 있다.
> * 시리즈, 단면의 특정 영역을 확대하거나 축소하여 볼 수 있다.

> ### 3D Modeling
> * 종양에 해당하는 영역을 감지하거나 수동으로 마킹할 수 있다.
> * 적층된 종양 단면으로부터 종양의 입체 모델을 생성할 수 있다.
> * 종양 모델을 렌더링, 회전 등 변환을 가할 수 있다.
> * 종양 모델을 파일(*.tmr)로 내보낼 수 있다.

> ### Analyzing
> * 종양 모델의 부피를 계산할 수 있다.
> * 촬영 시점이 다른 종양 모델을 파일(*.tmr)로부터 불러와 서로 비교할 수 있다.
> * 촬영 시점에 따른 종양의 부피 및 성장율을 그래프로 나타낼 수 있다.

> ### Etc.
> * 프로젝트를 파일(.bts)로 저장하고 불러와서 모델을 수정할 수 있다.
> * Help 메뉴로부터 사용 방법, 프로그램 정보를 확인할 수 있다.

 ## Project Overview
> ### Language
> Python (3.9.0 interpreter)

> ### IDE
> Visual Studio Code (1.95.3) 

> ### Framework
> Qt5 (5.15.11)
 
> ### GUI
> * 단일한 윈도우(MainWindow.py)가 존재한다.
> * 윈도우는 2개의 하위 Fragment 모듈들로 구성되며, 대부분의 동작은 각 Fragment가 처리한다.
> * LayersFragment 는 시리즈 및 단면 탐색, 종양 경계 입력을 수행한다.
> * RenderingFragment 는 3D 렌더링, 모델 변환(rotate, scale)을 수행한다.
 
> ### Architecture
> * MVVM Pattern
> * 단일한 뷰모델(ViewModel.py)이 존재한다.
> * Layer 간 결합도를 낮추기 위해 Observer 패턴을 사용하였다.
> * Observer 패턴의 구현을 위해 data와 callback을 갖는 LiveData 모듈을 작성하였다.
 
> ### 3D Graphics
> * 렌더링과 영상 처리에 각각 PyOpenGL(3.1.7), OpenCV(4.10.0), Open3d(0.18.0)를 사용하였다.
> * 종양의 경계를 결정하기 위해 단면 이미지에 Contour detection을 적용하였다. (사용자 수정 가능)
> * 입력된 종양 경계점을 적층하여 3D point cloud 를 구성하였다.
> * point cloud 로부터 mesh 를 얻는 계산에는 Poission reconstruction 이 적용되었다.
> * 종양 모델의 부피는 n번째 단면적 Sn, 단면간격 Δh에 대하여 V = Σ(Sn*Δh)로 결정하였다.
> * 단면적은 Shoelace formula 에 경계점을 입력하여 계산하였다.
> * 동일한 종양을 여러 개의 시리즈(Axial, Coronal, Sagittal)에서 마크한 경우, 모든 시리즈로부터 point cloud를 취한다.
> * 위 경우 각 시리즈가 서로의 단면 사이에 있는 공백을 보완해주므로 실제에 가까운 모델을 생성할 수 있다. (부피는 산술평균을 취한다)

 ## Author
 * 조성원 (Sung Won Jo)
 
     📧 waterbottle54@naver.com
   
     📚 [Portfolio](https://www.devsungwonjo.pe.kr/)
   
     📹 [YouTube Channel](https://github.com/waterbottle54)
   
 <img src="https://github.com/waterbottle54/tumor_simulator/blob/main/screenshots/demo-about.png" alt="My Image" width="70%">

 ## Version History
 * **1.01** (2023.4): 종양 렌더링 기능 구현
   
 * **1.02** (2023.5): 종양 성장 패턴 analyze 기능 구현

 * **1.03** (2024.12): 종양 경계 auto detection 구현

 ## Acknowledgments
 * Darcy Mason, Adit Panchal, MIT (pydicom: https://github.com/pydicom/pydicom)
 * Mike C. Fletcher (pyopengl: http://pyopengl.sourceforge.net)
 * Open3D Team (open3d: https://www.open3d.org)



