# Brain Tumor Simulator  


Tumor 3D Modeling          |  Tumor Growth Pattern
:-------------------------:|:-------------------------:
![](https://github.com/waterbottle54/tumor_simulator/blob/main/demo-model.png) | ![](https://github.com/waterbottle54/tumor_simulator/blob/main/demo-graph.png)


## Description

**Brain Tumor Simulator**는 **Qt5 / Python** 으로 작성된 의료 영상 소프트웨어입니다.

이 프로그램은 **DICOM** 데이터로부터 종양을 3D 모델로 나타내고, 부피(㎤) 등을 측정할 수 있습니다.

 :warning: *이 프로그램은 의료 진단을 대체하는 용도로는 사용될 수 없습니다.*


## Getting Started

### Dependencies

* Windows: **10, 11**

* macOS: **unidentified**

* python >= **3.0.9**

### Installing

* 방법1. Repository의 **Main.py**를 python 인터프리터(>=3.0.9)로 실행합니다. *(Consts.py 모듈의 debug_or_release 를 True 로 설정합니다.)*
  
* 방법2: 다음 링크에서 **실행파일**(.exe)을 다운로드 합니다. [BTS_exe.zip](https://drive.google.com/file/d/1jTMRluP4cpLhTS-4g9lGYfiC0SxKQW2w/view?usp=sharing)

>> *(Consts.py 모듈의 debug_or_release를 True로 설정하고 실행하십시오.)*


## Help

#### Basic Instruction

Move Camera: Left Button Drag

Zoom In/Out: Mouse Wheel

Mark Tumor: Right Button Drag

Change Layer: Ctrl + Mouse Wheel

Skip Layers: Page Up / Page Down

Skip All Layers: Home / End

Zoom 3D Tumor: Mouse Wheel

Rotate 3D Tumor: Mouse Drag

* Import folder that directly contains DICOM files.

* Importing may take up to two minutes.

* Project documents are *.bts files.

* Tumor object files are *.tmr files.


## Author

조성원 (Sung Won Jo)

:email: waterbottle54@naver.com

 [YouTube Channel](https://github.com/waterbottle54)

<img src="https://github.com/waterbottle54/tumor_simulator/blob/main/demo-about.png" alt="My Image" width="70%">


## Version History

* 1.01:
    * 종양 렌더링 기능 구현
* 1.02:
    * 종양 성장 패턴 analyze 기능 구현


## Acknowledgments

* Darcy Mason, Adit Panchal, MIT (pydicom library: https://github.com/pydicom/pydicom)




