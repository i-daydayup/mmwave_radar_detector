# mmwave_radar_detector
毫米波雷达检测，描述整个架构。

方案结构为：
```
[1] 射频前端（RF Front-End）  
     ↓（发射/接收电磁波）
[2] 模拟/数字转换与原始数据采集（ADC + Raw Data Capture）  
     ↓（输出IQ复数基带信号或中频信号）
[3] 雷达信号处理链（Signal Processing Chain） ←【核心！用Python仿真】
     ↓（输出目标列表：距离、速度、角度、SNR等）
[4] 应用层输出（Object List / Point Cloud / CAN消息等）
```
