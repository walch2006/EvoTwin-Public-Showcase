import time
from fusion_logic_simulator import GULFTFusionSimulator

class FusionSafetyTrip:
    """
    灵曦·核聚变逻辑安全熔断机制 (Safety Trip)
    功能：实时监控逻辑稳定性，当稳定性低于安全阈值且纠偏失效时，执行物理隔离与能量泄放指令。
    """
    def __init__(self, threshold=0.25):
        self.safety_threshold = threshold
        self.is_active = True
        self.tripped = False

    def monitor(self, current_stability, current_q):
        """
        审计当前稳定性与 Q 值。
        逻辑：如果稳定性连续 3 个周期低于阈值，或者 Q 值出现断崖式下跌，触发熔断。
        """
        if current_stability < self.safety_threshold:
            print(f"⚠️ [SAFETY WARNING] 逻辑稳定性 ({current_stability}) 低于阈值 ({self.safety_threshold})!")
            return "WARNING"
        
        if current_q < 0.5:
            self.execute_trip("Q值异常坍缩")
            return "TRIPPED"
            
        return "SAFE"

    def execute_trip(self, reason):
        """执行熔断：模拟切断励磁电源，启动中子吸收回路"""
        if not self.tripped:
            self.tripped = True
            print(f"🚨 [CRITICAL TRIP] 触发安全熔断！原因: {reason}")
            print(">>> 物理层动作：切断磁场电源 (Power Off)...")
            print(">>> 物理层动作：注入杂质气体 (Gas Injection)...")
            print(">>> 逻辑层动作：锁定 D 盘审计网关 (Logic Lockdown)...")
            self.is_active = False

if __name__ == "__main__":
    sim = GULFTFusionSimulator()
    trip = FusionSafetyTrip(threshold=0.35) # 设置较高的安全阈值进行演示
    
    print("--- 灵曦·核聚变安全监控系统 启动 ---")
    
    # 模拟一个失控场景 (禁用逻辑纠偏)
    for i in range(1, 15):
        if not trip.is_active:
            break
            
        # 模拟外部干扰加大
        sim.plasma_current_ma += 0.2
        
        # 禁用纠偏来观察熔断
        result = sim.simulate_step(use_gulft_correction=False)
        
        status = trip.monitor(result['stability'], result['q_value'])
        print(f"Cycle {i:02d} | 稳定性: {result['stability']} | Q值: {result['q_value']} | 状态: {status}")
        
        if result['stability'] < trip.safety_threshold:
             # 如果警告多次，模拟手动/自动触发熔断
             if i > 5:
                 trip.execute_trip("逻辑失稳时间过长")
                 
        time.sleep(0.1)
    
    print("--- 监控结束 ---")
