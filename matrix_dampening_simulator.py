import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from dataclasses import dataclass
from typing import Dict, Tuple, Optional


@dataclass
class SimulationConfig:
    """Конфигурация симуляции MATRIX v11.0"""
    duration: float = 5.0
    fs: int = 10000                    # Частота дискретизации (Гц)
    uncompensated_peak: float = 300.0
    compliance_ratio: float = 3.0      # 3:1 viscoelastic : rigid
    hunting_freq: float = 150.0        # Частота "охоты" (Гц)
    natural_freq: float = 0.8          # Низкочастотная составляющая
    viscoelastic_damping: float = 0.65 # Коэффициент вязкого демпфирования


class MatrixDampeningSimulator:
    """
    MATRIX v11.0 — Advanced Viscoelastic Compliance Inverter Dampening Framework
    Био-вдохновлённая модель с Kelvin-Voigt viscoelastic элементами.
    """
    
    def __init__(self, config: Optional[SimulationConfig] = None):
        self.config = config or SimulationConfig()
        self.ratio = self.config.compliance_ratio
        
    def kelvin_voigt_attenuation(self, force: np.ndarray, dt: float) -> np.ndarray:
        """Реальная вязкоупругая модель Kelvin-Voigt"""
        k = 1.0 + self.ratio * 0.4          # Жесткость
        eta = self.config.viscoelastic_damping * self.ratio * 0.8  # Вязкость
        
        # Численное решение дифференциального уравнения
        damped = np.zeros_like(force)
        damped[0] = force[0] / k
        
        for i in range(1, len(force)):
            damped[i] = (damped[i-1] + (dt * force[i] / eta)) / (1 + (dt * k / eta))
        
        return damped
    
    def simulate(self) -> Dict:
        """Запуск полной симуляции"""
        t = np.linspace(0, self.config.duration, int(self.config.duration * self.config.fs))
        dt = t[1] - t[0]
        
        # === Не скомпенсированный сигнал (реальная "охота" статора) ===
        raw = self.config.uncompensated_peak * np.exp(-0.35 * t) * \
              (1.0 + 0.32 * np.sin(2 * np.pi * self.config.hunting_freq * t))
        
        # Добавляем высокочастотный шум (реалистичный inverter noise)
        noise = 8.0 * np.random.randn(len(t)) * np.exp(-2.0 * t)
        raw += noise
        
        # === Применяем viscoelastic демпфирование ===
        viscoelastic_damped = self.kelvin_voigt_attenuation(raw, dt)
        
        # === Финальная компонента (низкочастотная + остаточные колебания) ===
        residual = 12.0 * np.sin(2 * np.pi * self.config.natural_freq * t) * np.exp(-1.2 * t)
        
        filtered = viscoelastic_damped + residual
        
        # === Анализ пиков ===
        peaks_raw, _ = find_peaks(raw, distance=50)
        peaks_filt, _ = find_peaks(filtered, distance=50)
        
        stats = {
            'raw_peak': float(np.max(raw)),
            'filtered_peak': float(np.max(filtered)),
            'peak_reduction_percent': (1 - np.max(filtered)/np.max(raw)) * 100,
            'settling_time': self._calculate_settling_time(t, filtered)
        }
        
        return {
            'time': t,
            'raw': raw,
            'filtered': filtered,
            'stats': stats,
            'peaks_raw': peaks_raw,
            'peaks_filt': peaks_filt
        }
    
    def _calculate_settling_time(self, t: np.ndarray, signal: np.ndarray, tolerance: float = 0.05) -> float:
        """Время выхода на 5% полосу"""
        final_value = np.mean(signal[-len(signal)//4:])
        within_band = np.abs(signal - final_value) < tolerance * self.config.uncompensated_peak
        if np.any(within_band):
            return float(t[np.where(within_band)[0][0]])
        return self.config.duration


# ====================== ЗАПУСК ======================
if __name__ == "__main__":
    config = SimulationConfig(
        duration=4.0,
        uncompensated_peak=300.0,
        compliance_ratio=3.2,
        viscoelastic_damping=0.72
    )
    
    sim = MatrixDampeningSimulator(config)
    result = sim.simulate()
    stats = result['stats']
    
    print("═" * 70)
    print("✅ MATRIX v11.0 — Viscoelastic Compliance Simulator")
    print("═" * 70)
    print(f"Соотношение  : {config.compliance_ratio}:1")
    print(f"Пик до       : {stats
