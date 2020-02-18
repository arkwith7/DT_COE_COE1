# COE1 파트 RPA Delivery Solution Repository
Enterprise RPA 구현시 Automation anywhere(이하 AA) 를 이용하여 기타 개발 기술들과 연계 확장을 위한 솔루션을 연구한다.

## 요구되는 Software 목록
1. AA Bot Creator 11.3
2. VSCode 또는 PyCharm
3. Git for Windows
4. Python 3.6 이상

## 설치방법
윈도우에서 cmd를 실행하여 `` C:\Users\"윈도우 사용자명"\Documents\Automation Anywhere Files `` 디렉토리로 이동하여
```
git init
git add *
git commit -m "first commit"
```
git 명령어로 local repository 생성하고
```
git remote add origin https://github.com/arkwith7/DT_COE_COE1.git
```
서버의 remote repository에 연결하고 나서
```
git fetch --all
git reset --hard origin/master
```
로 서버에 있는 모든 파일을 내려 받는다.

## Python 가상환경 설치
pip를 이용하여 vertualenv를 설치한다.
```
pip install vertualenv
```
그리고 AA에서 사용할 RPA를 위한 파이썬 가상환경을 만든다. 작업 디렉토리는 `` C:\Users\"윈도우 사용자명"\Documents\Automation Anywhere Files ``이다
```
virtualenv python_env
```
python_env라는 디렉토리가 생성되면 python_activate.bat 파일을 현재 디렉토리에서 실행한다.
```
python_activate.bat
```
명령어 프롬프트가 `` (PYTHON~1) C:\Users\"윈도우 사용자명"\Documents\Automation Anywhere Files> ''와 같이 바뀌면 파이썬 필요 패키지 설치를 위해 아래와 같이 작업 디렉토리를 변경한다.
```
(PYTHON~1) C:\Users\"윈도우 사용자명"\Documents\Automation Anywhere Files>cd DT_COE_COE1\Python_install_guide
```
이동한 디렉토리에서 [Python_Package_Install_Guide.txt](DT_COE_COE1\Python_install_guide\Python_Package_Install_Guide.txt)파일을 찾고 안의 내용이 안내 하는데로 파이썬 필요 패키지를 설치 한다.
