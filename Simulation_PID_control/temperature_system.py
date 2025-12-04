"""
Temperature System Simulation Module
온도 시스템 시뮬레이션과 실행 로직을 담당하는 모듈
"""

import numpy as np
from pid_controller import PIDController


class TemperatureSystem:
    """
    온도 시스템 시뮬레이션 (1차 시스템 모델)
    3D 프린터 핫엔드의 열적 특성을 간단히 모델링
    """
    
    def __init__(self, initial_temp=25, ambient_temp=25):
        """
        온도 시스템 초기화
        
        매개변수:
            initial_temp: 시작 온도 (°C)
            ambient_temp: 주변 온도 (°C)
        """
        self.temp = initial_temp        # 현재 온도
        self.ambient = ambient_temp     # 주변 온도 (실온)
        
        # 열적 특성 파라미터
        self.heat_capacity = 5.0        # 열 용량 (클수록 온도 변화 느림)
        self.cooling_rate = 0.03        # 냉각 계수 (클수록 빨리 식음)
        
        # 참고: 최대 도달 가능 온도 계산
        # 히터 100% 출력 시 평형 온도
        max_temp = self.ambient + (100.0 / self.heat_capacity) / self.cooling_rate
        
    def update(self, heater_power, dt):
        """
        온도 업데이트 - 물리 법칙 시뮬레이션
        
        매개변수:
            heater_power: 히터 출력 (0~100%)
            dt: 시간 간격 (초)
            
        반환값:
            현재 온도 (°C)
            
        물리 모델:
            온도 변화율 = (가열량 - 냉각량) / 열용량
            - 가열량: 히터 출력에 비례
            - 냉각량: (현재온도 - 주변온도)에 비례
        """
        # 1. 히터로 인한 온도 상승
        #    히터 출력이 클수록, 열 용량이 작을수록 빠르게 상승
        heating = heater_power / self.heat_capacity
        
        # 2. 자연 냉각 (주변 온도로 수렴)
        #    온도 차이가 클수록, 냉각 계수가 클수록 빠르게 식음
        cooling = self.cooling_rate * (self.temp - self.ambient)
        
        # 3. 온도 변화 = 가열 - 냉각
        self.temp += (heating - cooling) * dt
        
        return self.temp


def run_simulation(Kp, Ki, Kd, target_temp=200, sim_time=300):
    """
    PID 제어 시뮬레이션 실행 - 전체 과정 통합
    
    매개변수:
        Kp, Ki, Kd: PID 게인 값
        target_temp: 목표 온도 (°C)
        sim_time: 시뮬레이션 시간 (초)
        
    반환값:
        시뮬레이션 데이터를 담은 딕셔너리
    """
    # 1. 시뮬레이션 설정
    dt = 0.1  # 시간 간격 (0.1초마다 계산)
    time_steps = int(sim_time / dt)
    
    # 2. PID 제어기 생성
    pid = PIDController(Kp, Ki, Kd, setpoint=target_temp)
    
    # 3. 온도 시스템 생성 (실온 25도에서 시작)
    system = TemperatureSystem(initial_temp=25, ambient_temp=25)
    
    # 4. 데이터 저장용 리스트 초기화
    times = []
    temperatures = []
    setpoints = []
    heater_powers = []
    p_terms = []
    i_terms = []
    d_terms = []
    
    # 5. 시뮬레이션 메인 루프
    for i in range(time_steps):
        current_time = i * dt
        current_temp = system.temp
        
        # 5-1. PID 제어기로 히터 출력 계산
        control_output, P, I, D = pid.update(current_temp, dt)
        
        # 5-2. 히터 출력 제한 (0~100% 사이로 클리핑)
        #      실제로는 음수나 100% 이상 출력 불가능
        heater_power = np.clip(control_output, 0, 100)
        
        # 5-3. 시스템 업데이트 (물리 시뮬레이션)
        new_temp = system.update(heater_power, dt)
        
        # 5-4. 데이터 저장 (나중에 그래프 그리기 위해)
        times.append(current_time)
        temperatures.append(current_temp)
        setpoints.append(target_temp)
        heater_powers.append(heater_power)
        p_terms.append(P)
        i_terms.append(I)
        d_terms.append(D)
    
    # 6. 결과 데이터를 딕셔너리로 반환
    return {
        'times': times,
        'temperatures': temperatures,
        'setpoints': setpoints,
        'heater_powers': heater_powers,
        'p_terms': p_terms,
        'i_terms': i_terms,
        'd_terms': d_terms,
        'Kp': Kp,
        'Ki': Ki,
        'Kd': Kd
    }