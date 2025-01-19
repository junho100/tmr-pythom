from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import pyqtgraph as pg
from gdx import gdx
import time
import numpy as np

class BreathingVisualizer(QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.gdx = None  # 초기에는 None으로 설정
        self.data_buffer = []  # 빈 리스트로 초기화
        self.time_buffer = []  # 빈 리스트로 초기화
        self.start_time = 0
        self.buffer_size = 300  # Added for the buffer_size attribute
        self.initUI()
        
    def initUI(self):
        # 메인 윈도우 설정
        self.setWindowTitle('호흡 패턴 시각화')
        self.setGeometry(100, 100, 800, 600)
        
        # 중앙 위젯 생성
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 상단 컨트롤 패널
        control_panel = QHBoxLayout()
        
        # 사용자 ID 표시
        user_label = QLabel(f'사용자 ID: {self.user_id}', self)
        control_panel.addWidget(user_label)
        
        # 연결 버튼
        self.connect_btn = QPushButton('센서 연결', self)
        self.connect_btn.clicked.connect(self.connectSensor)
        control_panel.addWidget(self.connect_btn)
        
        # 시작/정지 버튼
        self.start_btn = QPushButton('측정 시작', self)
        self.start_btn.clicked.connect(self.toggleMeasurement)
        self.start_btn.setEnabled(False)
        control_panel.addWidget(self.start_btn)
        
        # 상태 표시 레이블
        self.status_label = QLabel('상태: 연결 대기중', self)
        control_panel.addWidget(self.status_label)
        
        layout.addLayout(control_panel)
        
        # 그래프 위젯 설정
        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setBackground('w')
        self.graph_widget.setTitle('실시간 호흡 패턴', color='k')
        self.graph_widget.setLabel('left', '호흡 깊이', color='k')
        self.graph_widget.setLabel('bottom', '시간 (초)', color='k')
        self.graph_widget.showGrid(x=True, y=True)
        layout.addWidget(self.graph_widget)
        
        # 호흡 시각화 패널
        self.breathing_indicator = QProgressBar()
        self.breathing_indicator.setMinimum(0)
        self.breathing_indicator.setMaximum(100)
        self.breathing_indicator.setOrientation(Qt.Vertical)
        self.breathing_indicator.setTextVisible(False)
        self.breathing_indicator.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                background-color: #FFFFFF;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 20px;
            }
        """)
        layout.addWidget(self.breathing_indicator)
        
        # 측정값 표시 레이블
        self.value_label = QLabel('현재 측정값: -', self)
        layout.addWidget(self.value_label)
        
        # 타이머 설정
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateData)
        
    def connectSensor(self):
        try:
            print("[연결 시도] 시작")
            
            # 이전 연결 정리
            if self.gdx:
                try:
                    self.gdx.stop()
                    self.gdx.close()
                    self.gdx = None
                except Exception as e:
                    print(f"[연결 해제 오류] {str(e)}")
                    pass
                
            # 새로운 연결 시도
            self.gdx = gdx.gdx()
            
            # 블루투스 장치 검색 및 연결
            print("[연결 시도] 블루투스 연결 시도")
            # 연결 전에 장치 검색
            discovered_devices = self.gdx.discover_ble_devices()
            if not discovered_devices:
                raise Exception("사용 가능한 블루투스 장치를 찾을 수 없습니다")
            
            # 첫 번째 발견된 장치 선택
            selected_device = discovered_devices[0][0]  # 장치 이름 가져오기
            
            # 장치 연결
            self.gdx.open(connection='ble', device_to_open=selected_device)
            print("open device success")
            
            # 센서 선택 전에 잠시 대기
            time.sleep(1)
            
            # gdx.py의 select_sensors 호출
            self.gdx.select_sensors([1])
            print("연결 성공")
            
            self.status_label.setText('상태: 연결됨')
            self.connect_btn.setEnabled(False)
            self.start_btn.setEnabled(True)
            print("[연결 시도] 연결 성공")
                
        except Exception as e:
            print(f"[연결 시도] 오류 발생: {str(e)}")
            if self.gdx:
                try:
                    self.gdx.close()
                except:
                    pass
                self.gdx = None
            error_msg = (
                "센서 연결 실패\n\n"
                "다음 사항을 확인해주세요:\n"
                "1. 센서의 전원이 켜져 있는지\n"
                "2. 블루투스가 활성화되어 있는지\n"
                "3. 센서가 다른 프로그램에 연결되어 있지 않은지"
            )
            QMessageBox.critical(self, '연결 오류', error_msg)
            self.connect_btn.setEnabled(True)
            self.start_btn.setEnabled(False)
            self.status_label.setText('상태: 연결 실패')
            
    def toggleMeasurement(self):
        if self.start_btn.text() == '측정 시작':
            self.startMeasurement()
        else:
            self.stopMeasurement()
            
    def startMeasurement(self):
        try:
            # 완전한 초기화
            self.data_buffer = []
            self.time_buffer = []
            self.graph_widget.clear()
            self.breathing_indicator.setValue(0)
            self.value_label.setText('현재 측정값: -')
            
            # gdx 초기화 및 재시작
            if self.gdx:
                try:
                    self.gdx.stop()  # 혹시 모를 이전 측정 정지
                except Exception as e:
                    print(f"[측정 시작] 이전 측정 정지 오류: {str(e)}")
                    pass
                
                print("[측정 시작] 센서 상태 확인")
                print(f"[측정 시작] enabled_sensors: {self.gdx.enabled_sensors}")
                print(f"[측정 시작] devices: {self.gdx.devices}")
                
                # 센서가 활성화되어 있지 않다면 다시 활성화
                if not self.gdx.enabled_sensors:
                    print("[측정 시작] 센서 재활성화 시도")
                    self.gdx.select_sensors([1])
                    
                self.gdx.start(period=100)  # 100ms 간격으로 데이터 수집
                
                # 데이터를 실제로 읽을 수 있는지 테스트
                test_measurements = self.gdx.read()
                print(f"[측정 시작] 테스트 측정값: {test_measurements}")
                if not test_measurements:
                    raise Exception("센서에서 데이터를 읽을 수 없습니다")
                    
                self.start_time = time.time()
                self.timer.start(100)  # 100ms 간격으로 업데이트
                self.start_btn.setText('측정 정지')
                self.status_label.setText('상태: 측정 중')
                
        except Exception as e:
            print(f"[측정 시작 오류] {str(e)}")
            self.stopMeasurement()
            QMessageBox.warning(self, '측정 오류', '측정을 시작할 수 없습니다.\n센서 연결을 확인해주세요.')
            
    def stopMeasurement(self):
        print("[측정 정지] 시작")
        self.timer.stop()
        try:
            if self.gdx:
                self.gdx.stop()
        except Exception as e:
            print(f"[측정 정지 오류] {str(e)}")
            pass
        
        # 버퍼가 None인지 확인하고 초기화
        if self.data_buffer is None:
            self.data_buffer = []
        if self.time_buffer is None:
            self.time_buffer = []
        
        # 버퍼 초기화 전 상태 출력
        print(f"[측정 정지] 버퍼 초기화 전 - data: {len(self.data_buffer) if self.data_buffer else 'empty'}, time: {len(self.time_buffer) if self.time_buffer else 'empty'}")
        
        # 버퍼 비우기
        self.data_buffer.clear()
        self.time_buffer.clear()
        
        # 버퍼 초기화 후 상태 출력
        print(f"[측정 정지] 버퍼 초기화 후 - data: {len(self.data_buffer)}, time: {len(self.time_buffer)}")
        
        self.breathing_indicator.setValue(0)
        self.value_label.setText('현재 측정값: -')
        self.graph_widget.clear()
        
        self.start_btn.setText('측정 시작')
        self.status_label.setText('상태: 대기 중')
        print("[측정 정지] 완료")
        
    def updateData(self):
        try:
            # 먼저 연결 상태 확인
            if not self.gdx:
                raise Exception("연결이 끊어졌습니다")
            
            measurements = self.gdx.read()
            print(f"[데이터 업데이트] measurements: {measurements}, 타입: {type(measurements)}")
            
            if not measurements:  # None이거나 빈 리스트인 경우
                # 연결이 끊어졌는지 확인
                found_devices = self.gdx.godirect.list_devices()
                if not found_devices:
                    raise Exception("연결이 끊어졌습니다")
                print("[데이터 업데이트] 데이터 없음")
                return
            
            print(f"[데이터 업데이트] measurements 길이: {len(measurements)}")
            
            try:
                value = measurements[0]
                print(f"[데이터 업데이트] 첫 번째 값: {value}, 타입: {type(value)}")
            except (IndexError, TypeError) as e:
                print(f"[데이터 업데이트] 데이터 형식 오류: {e}")
                print(f"[데이터 업데이트] measurements 상세: {measurements}")
                return
            
            current_time = time.time() - self.start_time
            
            # 유효한 데이터인지 확인
            if value is not None:
                print(f"[데이터 업데이트] 버퍼 추가 전 길이 - data: {len(self.data_buffer)}, time: {len(self.time_buffer)}")
                self.data_buffer.append(value)
                self.time_buffer.append(current_time)
                print(f"[데이터 업데이트] 버퍼 추가 후 길이 - data: {len(self.data_buffer)}, time: {len(self.time_buffer)}")
                
                if len(self.time_buffer) > self.buffer_size:
                    print("[데이터 업데이트] 버퍼 크기 초과, 첫 번째 항목 제거")
                    self.data_buffer.pop(0)
                    self.time_buffer.pop(0)
                
                # 그래프 업데이트
                if self.data_buffer and self.time_buffer:
                    try:
                        self.graph_widget.clear()
                        self.graph_widget.plot(self.time_buffer, self.data_buffer, pen=pg.mkPen('b', width=2))
                    except Exception as e:
                        print(f"[데이터 업데이트] 그래프 업데이트 오류: {e}")
                
                try:
                    normalized_value = min(100, max(0, value * 2))
                    self.breathing_indicator.setValue(int(normalized_value))
                    self.value_label.setText(f'현재 측정값: {value:.2f}')
                except Exception as e:
                    print(f"[데이터 업데이트] 표시 업데이트 오류: {e}")
                
        except Exception as e:
            print(f"[데이터 업데이트] 오류 발생: {str(e)}")
            print(f"[데이터 업데이트] 오류 타입: {type(e)}")
            print(f"[데이터 업데이트] 현재 버퍼 상태 - data: {len(self.data_buffer) if self.data_buffer else 'None'}, time: {len(self.time_buffer) if self.time_buffer else 'None'}")
            
            # 연결 해제 처리
            self.stopMeasurement()
            self.status_label.setText('상태: 연결 끊김')
            self.connect_btn.setEnabled(True)
            self.start_btn.setEnabled(False)
            
            # 버퍼와 표시 초기화
            self.data_buffer = []
            self.time_buffer = []
            self.breathing_indicator.setValue(0)
            self.value_label.setText('현재 측정값: -')
            self.graph_widget.clear()
            
            QMessageBox.warning(self, '연결 오류', '센서와의 연결이 끊어졌습니다.')
            
    def closeEvent(self, event):
        self.stopMeasurement()
        if self.gdx:
            try:
                self.gdx.stop()
                self.gdx.close()
                self.gdx = None
            except Exception:
                pass
        event.accept()
