# 产生雷达信号，作为激励源送给phthon处理模块，验证功能
import numpy as np
import matplotlib.pyplot as plt

# 雷达天线，1发2收天线，其中2个接收天线水平放置，间距94mm。每个Chirp采样点256，64个Chirp。
# 被检测目标距离雷达100米，速度5m/s正对雷达飞线，角度为0°。根据这个信息，使用python语言产生
# 激励信号。激励数据为复数形式，实部和虚部均使用16位定点数表示。

# 雷达参数
fc = 77e9          # 载频 77 GHz
c = 3e8            # 光速
B = 1e9            # 带宽 1 GHz
T = 100e-6         # Chirp 周期 100 µs
fs = 20e6          # ADC 采样率 20 MHz
Ns = 256           # 每 Chirp 采样点数
Nchirp = 64        # Chirp 数
d = 0.094          # 接收天线间距 94 mm

# 目标参数
R0 = 100           # 距离 100 m
v = 5              # 速度 5 m/s，正对雷达
theta = 0          # 角度 0°

# 生成快时间轴和慢时间轴
t_fast = np.arange(Ns) / fs                    # 单 Chirp 内时间
t_slow = np.arange(Nchirp) * T                 # Chirp 间时间

# 目标引入的时延和多普勒
tau0 = 2 * R0 / c                              # 双程时延
fd = 2 * v * fc / c                            # 多普勒频移

# 发射 Chirp 信号
St = np.exp(1j * 2 * np.pi * (fc * t_fast + 0.5 * B / T * t_fast ** 2))

# 两个接收通道的回波
Srx1 = np.zeros((Ns, Nchirp), dtype=complex)
Srx2 = np.zeros((Ns, Nchirp), dtype=complex)

for m in range(Nchirp):
    # 当前 Chirp 时刻的目标距离
    Rm = R0 - v * t_slow[m]
    taum = 2 * Rm / c
    # 相位包含时延和多普勒
    phase = 2 * np.pi * (fc * (t_fast - taum) +
                         0.5 * B / T * (t_fast - taum) ** 2) + \
            2 * np.pi * fd * t_slow[m]
    echo = np.exp(1j * phase)
    # 通道1（参考）
    Srx1[:, m] = echo
    # 通道2，因 theta=0，波程差为0，故与通道1相同
    Srx2[:, m] = echo

# 合并为 2 通道接收信号（激励源）
rx_signal = np.stack((Srx1, Srx2), axis=0)   # shape: (2, Ns, Nchirp)

# 将复数信号转换为16位定点数格式（实部和虚部分开）
# 归一化到 [-1, 1] 范围，然后缩放到 int16 范围 [-32768, 32767]
rx_signal_flat = rx_signal.reshape(-1)  # 展平为一维数组
real_part = np.int16(np.real(rx_signal_flat) * 32767)
imag_part = np.int16(np.imag(rx_signal_flat) * 32767)

# 交替存储实部和虚部：[real0, imag0, real1, imag1, ...]
sti_data = np.empty((len(rx_signal_flat) * 2,), dtype=np.int16)
sti_data[0::2] = real_part
sti_data[1::2] = imag_part

# 保存到 sti_data.txt 文件
output_file = 'sti_data.txt'
with open(output_file, 'w') as f:
    for i, value in enumerate(sti_data):
        f.write(f'{value:5d}')
        if (i + 1) % 16 == 0:  # 每行16个数据
            f.write('\n')
        else:
            f.write(' ')

print(f'Stimulus data saved to {output_file}')
print(f'Data points: {len(sti_data)} (real + imaginary)')
print(f'Original complex samples: {len(rx_signal_flat)}')

