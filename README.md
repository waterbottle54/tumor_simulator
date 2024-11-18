# Brain Tumor Simulator

Brain Tumor Simulator는 Qt5 / Python 으로 작성된 의료 영상 소프트웨어입니다.

이 프로그램은 종양을 3D 모델로 나타내고 그 부피 등을 측정할 수 있습니다.

(의료 진단을 대체하는 용도로 사용될 수 없습니다.)

실행파일(.exe)은 아래의 링크에서 다운받을 수 있습니다. 

(Consts.py 모듈의 debug_or_release를 True로 설정하고 실행하십시오.)

[Google Drive - EXE.zip](https://drive.google.com/file/d/1jTMRluP4cpLhTS-4g9lGYfiC0SxKQW2w/view?usp=sharing)






## Description

종양의 입체적 구조를 확인하고 정확한 부피 측정을 통해 병의 진행을 가늠할 수 있도록 개발된 QT Desktop Application입니다.
DICOM 파일을 읽어들인 후, 종양의 경계를 이루는 point cloud를 구성하고, 3D 모델을 빌드하여 종양의 구조를 파악합니다. 
내부 체적을 계산하고, OpenGL을 이용해 3D rendering 합니다. (체적 계산에는 shoelace formula로 얻은 단면의 넓이를 구분구적함) 
기존에 종양 모델을 볼록껍질(Convex hull)로 계산하였으나, 종양 표면의 요철을 반영하지 못하는 문제가 있었습니다. 
오차를 감소시키기 위해 Poisson reconstruction algorithm을 적용한 결과 품질이 개선됨. 

## Getting Started

### Dependencies

Windows 10, 11
(macOS 작동 여부는 미확인)

### Installing

* 선택 1. 이 repository에서 소스코드를 받아서 python 인터프리터로 실행합니다. (실행하기 전에, Consts.py 안의 debug_or_release==True인지 확인합니다.)
* 선택 2: 다음 링크에서 실행파일을 다운로드하고 압축을 해제합니다. https://drive.google.com/file/d/1jTMRluP4cpLhTS-4g9lGYfiC0SxKQW2w/view?usp=sharing


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

## Authors

Contributors names and contact info

조성원 (Sung Won Jo)
[waterbottle54@naver.com]

## Version History

* 1.00
    * 종양 렌더링 기능 구현
* 1.01
    * 종양 성장패턴 확인 기능 구현

## Acknowledgments

* Darcy Mason, Adit Panchal, MIT (pydicom library: https://github.com/pydicom/pydicom)




