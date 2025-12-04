"""
PID Controller Module
PID 제어기 계산만 담당하는 모듈
"""

class PIDController:
    """
    PID 제어기 클래스
    -P(비례): 현재 오차에 비례해서 반응
    -I(적분): 과거 오차를 누적하여 정상상태 오차 제거
    -D(미분): 오차의 변화율로 미래를 예측해서 오버슈트 감소
    """
    
    def __init__(self, Kp, Ki, Kd, setpoint=0.0):
        """
        PID 제어기 초기화
        
        매개변수:
        Kp: 비례 게인
        ki: 적분 게인
        Kd: 미분 게인
        setpoint: 목표값
        """
        # PID 게인값 설정
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        
        #목표값 설정
        self.setpoint = setpoint  

        # 내부 상태 변수 (계산 과정에서 사용)
        self.integral = 0.0       # 적분 누적값 
        self.prev_error = 0.0     # 이전 오차 (미분 계산용)

    def update(self, current_value, dt):
        """
        PID 제어 출력 계산
        
        매개변수:
        current_value: 현재 측정값
        dt: 시간 간격
        
        반환값:
        제어 출력 값
        """

        # 오차 계산 = 목표값 - 현재값
        error = self.setpoint - current_value
        
        # 2. P (비례 항) - 현재 오차에 비례
        # 오차가 크면 큰 출력, 작으면 작은 출력
        P = self.Kp * error
        
        #3. I(적분 항) - 오차를 시간에 따라 누적
        #   과거의 모든 오차를 더함 -> 정상상태 오차 제거
        self.integral += error * dt
        I = self.Ki * self.integral
        
        #4. D (미분 항) - 오차의 변화율로
        # 오차가 빠르게 변하면 미리 대응 -> 오버슈트 감소
        if dt > 0:
            derivative = (error - self.prev_error) / dt
        else:
            derivative = 0
        D = self.Kd * derivative
        
        #5. 다음 계산을 위해 현재 오차 저장
        self.prev_error = error
        
        #6. PID 출력 = P + I + D
        output = P + I + D
        
        return output, P, I, D
        
    def reset(self):
        """
        PID 제어기 초기화 (적분, 미분 항 리셋)
        시뮬레이션을 다시 시작할 떄 사용
        """
        self.integral = 0
        self.prev_error = 0