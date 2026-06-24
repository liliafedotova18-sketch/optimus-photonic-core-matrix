"""
Bio-Inspired Proprioception Gait Engine
Simplified simulation for research purposes only.
Based on principles of human neurophysiology and 3D biodynamics.
"""

import numpy as np

class ProprioceptionGaitEngine:
    """Simplified real-time proprioception simulator"""
    
    def __init__(self, sampling_rate=1000):
        self.sampling_rate = sampling_rate
        self.dt = 1.0 / sampling_rate
    
    def simulate_gait(self, duration=5.0):
        """Simulate joint movement and proprioceptive feedback"""
        t = np.arange(0, duration, self.dt)
        
        # Simulated joint angle
        angle = 0.6 * np.sin(2 * np.pi * 0.9 * t) + 0.3 * np.cos(2 * np.pi * 2.2 * t)
        
        # Simulated torque
        torque = 15.0 * np.sin(2 * np.pi * 0.9 * t) + np.random.normal(0, 1.2, len(t))
        
        # Virtual sensor signal (like FBG)
        sensor = angle * 950 + torque * 28 + np.random.normal(0, 12, len(t))
        
        return {
            'time': t,
            'joint_angle': angle,
            'torque': torque,
            'sensor_signal': sensor
        }
    
    def process_signal(self, sensor_signal):
        """Simple state estimation"""
        angle_est = sensor_signal / 980
        torque_est = (sensor_signal - angle_est * 950) / 28
        return angle_est, torque_est


# Demo
if __name__ == "__main__":
    engine = ProprioceptionGaitEngine(sampling_rate=1000)
    data = engine.simulate_gait(duration=3.0)
    
    print(f"✅ Simulation completed: {len(data['time'])} samples")
    print(f"Angle range: {data['joint_angle'].min():.3f} — {data['joint_angle'].max():.3f} rad")
