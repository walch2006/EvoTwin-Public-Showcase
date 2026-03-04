import hashlib
import hmac
import struct
import time
from typing import Dict, Any

class LSDPHandler:
    """
    灵曦·逻辑主权数据协议 (LSDP) 处理器 v1.0
    功能：实现逻辑种子加密、数据报文封装与主权验证。
    """
    def __init__(self, logic_seed: str):
        # 逻辑种子：基于 GULFT 核心公理的 SHA-256 哈希
        self.root_seed = hashlib.sha256(logic_seed.encode()).digest()
        self.protocol_header = b'LSDP'

    def generate_dynamic_key(self, timestamp: int) -> bytes:
        """基于时间戳生成动态交互密钥"""
        return hmac.new(self.root_seed, struct.pack('>Q', timestamp), hashlib.sha256).digest()

    def pack_data(self, phi: float, biases: Dict[str, float], command_vector: list) -> bytes:
        """
        按照 LSDP 规范封装报文
        报文结构：Header(4) + Timestamp(8) + Phi(32) + Bias(24) + Command(16) + Audit(32) + Checksum(4)
        """
        timestamp = int(time.time_ns())
        dynamic_key = self.generate_dynamic_key(timestamp)
        
        # 1. 逻辑场强参数 Φ 加密 (此处简化为 XOR 加密，实际应用中使用更复杂的流加密)
        phi_bytes = struct.pack('>d', phi).ljust(32, b'\0')
        encrypted_phi = bytes([b ^ k for b, k in zip(phi_bytes, dynamic_key)])
        
        # 2. 三维偏置向量 (Plasma/Field/Energy)
        bias_bytes = struct.pack('>ddd', biases.get('plasma', 0), biases.get('field', 0), biases.get('energy', 0))
        
        # 3. 0.1ms 预补偿指令 (反向磁场向量)
        command_bytes = struct.pack('>dd', command_vector[0], command_vector[1])
        
        # 4. 逻辑审计摘要 (HMAC 签名)
        audit_payload = encrypted_phi + bias_bytes + command_bytes
        audit_hash = hmac.new(dynamic_key, audit_payload, hashlib.sha256).digest()
        
        # 5. 组装报文
        packet = (
            self.protocol_header + 
            struct.pack('>Q', timestamp) + 
            encrypted_phi + 
            bias_bytes + 
            command_bytes + 
            audit_hash
        )
        
        # 6. 计算 CRC32 校验码
        import zlib
        checksum = struct.pack('>I', zlib.crc32(packet))
        
        return packet + checksum

    def verify_and_unpack(self, packet: bytes) -> Dict[str, Any]:
        """验证报文并解析数据"""
        if len(packet) < 120:  # 最小报文长度校验
            raise ValueError("LSDP Packet Too Short")
        
        if packet[:4] != self.protocol_header:
            raise ValueError("Invalid LSDP Header")
            
        # 提取各个字段
        timestamp = struct.unpack('>Q', packet[4:12])[0]
        encrypted_phi = packet[12:44]
        bias_bytes = packet[44:68]
        command_bytes = packet[68:84]
        audit_hash = packet[84:116]
        checksum = struct.unpack('>I', packet[116:120])[0]
        
        # 验证 CRC32
        import zlib
        if zlib.crc32(packet[:116]) != checksum:
            raise ValueError("LSDP Checksum Mismatch")
            
        # 生成动态密钥进行解密和签名验证
        dynamic_key = self.generate_dynamic_key(timestamp)
        
        # 验证签名
        audit_payload = encrypted_phi + bias_bytes + command_bytes
        expected_hash = hmac.new(dynamic_key, audit_payload, hashlib.sha256).digest()
        if not hmac.compare_digest(audit_hash, expected_hash):
            raise ValueError("LSDP Audit Signature Invalid (Sovereignty Breach Detected!)")
            
        # 解密 Φ
        phi_bytes = bytes([b ^ k for b, k in zip(encrypted_phi, dynamic_key)])
        phi = struct.unpack('>d', phi_bytes[:8])[0]
        
        # 解析偏置和指令
        biases = struct.unpack('>ddd', bias_bytes)
        commands = struct.unpack('>dd', command_bytes)
        
        return {
            "timestamp": timestamp,
            "phi": phi,
            "biases": {"plasma": biases[0], "field": biases[1], "energy": biases[2]},
            "commands": [commands[0], commands[1]]
        }

if __name__ == "__main__":
    # 模拟一次 LSDP 交互
    logic_seed = "GULFT_AXIOM_RESONANCE_SEED_2026"
    handler = LSDPHandler(logic_seed)
    
    # 封装数据
    phi = 232.65
    biases = {"plasma": 0.0151, "field": 0.0574, "energy": 0.1}
    commands = [0.45, -0.12]
    
    packet = handler.pack_data(phi, biases, commands)
    print(f"LSDP Packet Generated: {len(packet)} bytes")
    print(f"Hex: {packet.hex()[:64]}...")
    
    # 解析验证
    try:
        data = handler.verify_and_unpack(packet)
        print("--- LSDP Packet Verified Successfully ---")
        print(f"Phi: {data['phi']} | Commands: {data['commands']}")
    except Exception as e:
        print(f"LSDP Verification Failed: {e}")
