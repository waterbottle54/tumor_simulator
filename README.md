# Brain Tumor Simulator

이 응용프로그램은 DICOM 데이터에 촬영되어 있는 종양의 
입체적 생김새와 부피를 알기 위한 목적으로 작성되었습니다.

종양의 진행을 알 수 있도록, 다른 시간에 촬영된 종양 간의 육안 비교 및 
시계열적 성장패턴 분석 기능이 포함되어 있습니다.

This application is developed for tumor 3D modeling, volume measurement, 
comparison, and time series analysis.

## Description

사용 기술: Qt5, OpenGL, Open3d, MVVM Architecture 

가까운 사람의 암 투병 중, 종양의 입체적 구조를 확인하고 
정확한 부피 측정을 통해 병의 진행을 가늠할 수 있도록 개인적으로 개발한 QT Desktop Application입니다.

DICOM 파일을 읽어 들인 후, 종양의 경계를 이루는 point cloud를 구성하고, 3D 모델을 빌드하여 종양의 구조를 파악합니다. 
내부 체적을 계산하고 및 OpenGL 3d rendering하였습니다. 체적 계산에는 shoelace formula로 얻은 단면의 넓이를 구분구적하는 방식이 사용되었습니다. 
기존에 종양 모델을 볼록껍질(Convex hull)로 계산하였으나, 종양 표면의 요철을 반영하지 못하는 문제가 있었습니다. 오차를 감소시키기 위해 3D data processing 분야를 조사하여 Poisson reconstruction algorithm을 적용한 결과 목표한 품질을 달성할 수 있었습니다. 
micro-CT 생명공학 모델링을 연구하는 학생의 요청으로 본 프로그램의 소스코드를 제공한 바 있습니다. 의료와 소프트웨어를 접목시키는 이러한 경험을 통해 디지털 헬스케어 분야의 이로움에 주목하였고, 해당 분야에 기여하고자 하는 목표를 갖게 되었습니다.


## Getting Started

### Dependencies

* Describe any prerequisites, libraries, OS version, etc., needed before installing program.
* ex. Windows 10

### Installing

* How/where to download your program
* Any modifications needed to be made to files/folders

### Executing program

* How to run the program
* Step-by-step bullets
```
code blocks for commands
```

## Help

Any advise for common problems or issues.
```
command to run if program contains helper info
```

## Authors

Contributors names and contact info

ex. Dominique Pizzie  
ex. [@DomPizzie](https://twitter.com/dompizzie)

## Version History

* 0.2
    * Various bug fixes and optimizations
    * See [commit change]() or See [release history]()
* 0.1
    * Initial Release

## License

This project is licensed under the [NAME HERE] License - see the LICENSE.md file for details

## Acknowledgments

Inspiration, code snippets, etc.
* [awesome-readme](https://github.com/matiassingers/awesome-readme)
* [PurpleBooth](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2)
* [dbader](https://github.com/dbader/readme-template)
* [zenorocha](https://gist.github.com/zenorocha/4526327)
* [fvcproductions](https://gist.github.com/fvcproductions/1bfc2d4aecb01a834b46)

https://drive.google.com/file/d/1jTMRluP4cpLhTS-4g9lGYfiC0SxKQW2w/view?usp=sharing


