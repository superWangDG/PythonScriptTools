import os
import random



def generate_fixed_pattern_firmware(file_path="test_firmware.bin", size_mb=2):
    size = size_mb * 1024 * 1024
    pattern = [0xAA, 0x55]  # 交替模式
    with open(file_path, "wb") as f:
        for i in range(size):
            f.write(bytes([pattern[i % 2]]))
    print(f"生成 {file_path} 成功，大小: {os.path.getsize(file_path)} 字节")

if __name__ == "__main__":
    generate_fixed_pattern_firmware()