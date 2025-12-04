"""
UI and Plotting Module
그래프 출력, 성능 분석, 메인 실행을 담당하는 모듈
"""

import numpy as np
import matplotlib.pyplot as plt
import platform
from temperature_system import run_simulation


def setup_korean_font():
    """
    운영체제에 맞는 한글 폰트 설정
    Windows, macOS, Linux에서 각각 다른 폰트 사용
    """
    system = platform.system()
    
    # 운영체제별 한글 폰트 설정
    if system == 'Windows':
        font_name = 'Malgun Gothic'  # 맑은 고딕
    elif system == 'Darwin':  # macOS
        font_name = 'AppleGothic'
    else:  # Linux
        # Linux에서 사용 가능한 한글 폰트 시도
        font_candidates = ['NanumGothic', 'Noto Sans CJK KR', 
                          'Noto Sans KR', 'DejaVu Sans']
        font_name = font_candidates[0]
        
        # 설치된 폰트 확인
        import matplotlib.font_manager as fm
        available_fonts = [f.name for f in fm.fontManager.ttflist]
        
        for font in font_candidates:
            if font in available_fonts:
                font_name = font
                break
    
    # matplotlib에 폰트 적용
    plt.rc('font', family=font_name)
    plt.rc('axes', unicode_minus=False)  # 마이너스 기호 깨짐 방지
    
    print(f"폰트 설정: {font_name}\n")


def plot_results(data):
    """
    시뮬레이션 결과 그래프 출력
    
    매개변수:
        data: run_simulation()에서 반환된 딕셔너리
    """
    # 데이터 추출
    times = data['times']
    temps = data['temperatures']
    setpoints = data['setpoints']
    powers = data['heater_powers']
    p_terms = data['p_terms']
    i_terms = data['i_terms']
    d_terms = data['d_terms']
    Kp = data['Kp']
    Ki = data['Ki']
    Kd = data['Kd']
    
    # Figure 생성 (3개의 서브플롯)
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    fig.suptitle(f'PID 제어 시뮬레이션 (Kp={Kp}, Ki={Ki}, Kd={Kd})', 
                 fontsize=14)
    
    # --- 1. 온도 그래프 ---
    axes[0].plot(times, temps, 'b-', label='현재온도', linewidth=2)
    axes[0].plot(times, setpoints, 'r--', label='목표온도', linewidth=2)
    axes[0].set_ylabel('온도 (°C)', fontsize=12)
    axes[0].legend(loc='best')
    axes[0].grid(True, alpha=0.3)
    axes[0].set_title('온도 변화')
    
    # --- 2. 히터 출력 그래프 ---
    axes[1].plot(times, powers, 'g-', linewidth=2)
    axes[1].set_ylabel('히터 출력 (%)', fontsize=12)
    axes[1].grid(True, alpha=0.3)
    axes[1].set_title('제어 출력 (PWM 신호 크기)')
    axes[1].set_ylim([-5, 105])
    
    # --- 3. PID 각 항 그래프 ---
    axes[2].plot(times, p_terms, 'r-', label='P (비례)', alpha=0.7)
    axes[2].plot(times, i_terms, 'b-', label='I (적분)', alpha=0.7)
    axes[2].plot(times, d_terms, 'g-', label='D (미분)', alpha=0.7)
    axes[2].set_xlabel('시간 (초)', fontsize=12)
    axes[2].set_ylabel('기여도', fontsize=12)
    axes[2].legend(loc='best')
    axes[2].grid(True, alpha=0.3)
    axes[2].set_title('PID 각 항의 기여도')
    
    plt.tight_layout()
    plt.show()


def print_performance(data):
    """
    성능 지표 출력 및 분석
    
    매개변수:
        data: run_simulation()에서 반환된 딕셔너리
    """
    times = data['times']
    temps = np.array(data['temperatures'])
    setpoints = np.array(data['setpoints'])
    errors = setpoints - temps
    
    # --- 1. 정상 상태 도달 시간 계산 ---
    # 목표값의 ±2% 이내에 들어오면 정상 상태로 간주
    tolerance = setpoints[0] * 0.02
    steady_state_idx = None
    
    for i in range(len(errors)):
        if abs(errors[i]) <= tolerance:
            # 이후로 계속 범위 내에 있는지 확인 (50개 샘플)
            check_length = min(50, len(errors) - i)
            if all(abs(errors[i:i+check_length]) <= tolerance):
                steady_state_idx = i
                break
    
    # --- 출력 시작 ---
    print("\n" + "=" * 50)
    print("성능 지표 분석")
    print("=" * 50)
    
    # 정상 상태 도달 시간
    if steady_state_idx:
        print(f"정상상태 도달 시간: {times[steady_state_idx]:.1f}초")
    else:
        print("정상상태 도달 시간: 측정 불가 (목표에 수렴하지 못함)")
    
    # --- 2. 최대 오버슈트 ---
    # 목표값을 넘어선 최대 온도
    overshoot = np.max(temps) - setpoints[0]
    overshoot_percent = (overshoot / setpoints[0]) * 100
    print(f"최대 오버슈트: {overshoot:.1f}°C ({overshoot_percent:.1f}%)")
    
    # --- 3. 평균 제곱 오차 (MSE) ---
    # 전체 시뮬레이션 동안의 평균 오차
    mse = np.mean(errors**2)
    print(f"평균 제곱 오차 (MSE): {mse:.2f}")
    print("=" * 50 + "\n")


def main():
    """
    메인 실행 함수
    """
    # 한글 폰트 설정
    setup_korean_font()
    
    # 시작 메시지
    print("=" * 50)
    print("PID 제어 시뮬레이터")
    print("=" * 50)
    print("\n3D 프린터 핫엔드 온도 제어 시뮬레이션")
    print("목표: 실온 25°C에서 200°C까지 가열\n")
    
    # ===== 여기서 PID 값을 조정하세요! =====
    Kp = 5.0   # 비례 게인 - 클수록 빠르게 반응, 오버슈트 증가
    Ki = 0.1    # 적분 게인 - 정상상태 오차 제거, 너무 크면 진동
    Kd = 1.0    # 미분 게인 - 오버슈트 감소, 너무 크면 노이즈에 민감
    # =======================================
    
    print(f"현재 PID 값: Kp={Kp}, Ki={Ki}, Kd={Kd}\n")
    print("시뮬레이션 시작...\n")
    
    # 시뮬레이션 실행
    data = run_simulation(Kp=Kp, Ki=Ki, Kd=Kd, 
                         target_temp=200, sim_time=300)
    
    # 그래프 출력
    plot_results(data)
    
    # 성능 지표 출력
    print_performance(data)
    
    # 사용법 안내
    print("\n다른 PID 값을 시도하려면:")
    print("1. 코드에서 Kp, Ki, Kd 값을 수정")
    print("2. 다시 실행\n")
    print("권장 실험:")
    print("- P만 사용: Ki=0, Kd=0")
    print("- PI 제어: Kd=0")
    print("- PID 제어: 세 값 모두 조정")


# 이 파일을 직접 실행했을 때만 main() 함수 실행
# 다른 파일에서 import 했을 때는 실행 안 됨
if __name__ == "__main__":
    main()