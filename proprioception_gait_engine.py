import math
import json

class PhotonicGaitProprioceptionEngine:
    def __init__(self):
        # Parametri fisici del sensore ottico a reticolo di Bragg (FBG)
        self.central_wavelength_nm = 1550.0   # Lunghezza d'onda centrale del laser C-band
        self.gauge_factor_fbg = 1.2            # Coefficiente di sensibilità alla deformazione ottica
        
        # Limiti cinematici articolazione Optimus (es. Ginocchio / Knee Joint)
        self.max_knee_flexion_rad = 2.4        # Circa 137 gradi di flessione massima
        self.torque_constant_nm_per_strain = 45000.0 # Rigidità torsionale dinamica del Core in Zylon

    def process_gait_telemetry(self, shift_plus_45_pm, shift_minus_45_pm):
        """
        Decodifica i vettori di forza differenziali dal pattern incrociato Polar-Weave.
        Riceve lo spostamento dello spettro ottico in picometri (pm).
        """
        # 1. Converti lo spostamento ottico (picometri) in deformazione adimensionale (Microstrain)
        strain_plus_45 = (shift_plus_45_pm / 1000.0) / (self.central_wavelength_nm * self.gauge_factor_fbg)
        strain_minus_45 = (shift_minus_45_pm / 1000.0) / (self.central_wavelength_nm * self.gauge_factor_fbg)
        
        # 2. Algoritmo differenziale per disaccoppiare i vettori del cammino
        # La flessione lineare del giunto somma le deformazioni su entrambe le eliche
        bending_strain_vector = (strain_plus_45 + strain_minus_45) / 2.0
        
        # La torsione (rotazione parassita del tendine) genera una differenza di segno tra le eliche
        torsional_strain_vector = (strain_plus_45 - strain_minus_45) / 2.0
        
        # 3. Traduzione in metriche cinematiche reali per l'anello di controllo del robot
        calculated_joint_angle_rad = bending_strain_vector * 1200.0 # Scalatura cinematica basata sul raggio del giunto
        calculated_torque_nm = torsional_strain_vector * self.torque_constant_nm_per_strain
        
        # Vincolo di sicurezza software (Saturazione dei limiti articolari)
        if calculated_joint_angle_rad > self.max_knee_flexion_rad:
            calculated_joint_angle_rad = self.max_knee_flexion_rad
            
        return {
            "RAW_OPTICAL_INPUTS": {
                "Helix_Plus_45_Shift_pm": shift_plus_45_pm,
                "Helix_Minus_45_Shift_pm": shift_minus_45_pm
            },
            "DISCOUPLED_STRAIN_VECTORS": {
                "Pure_Bending_Microstrain": round(bending_strain_vector * 1e6, 2),
                "Pure_Torsion_Microstrain": round(torsional_strain_vector * 1e6, 2)
            },
            "HUMANOID_GAIT_FEEDBACK_4KHZ": {
                "Calculated_Joint_Angle_Radians": round(calculated_joint_angle_rad, 4),
                "Calculated_Joint_Angle_Degrees": round(math.degrees(calculated_joint_angle_rad), 2),
                "Active_Torsional_Torque_Nm": round(calculated_torque_nm, 3)
            }
        }

if __name__ == "__main__":
    engine = PhotonicGaitProprioceptionEngine()
    
    print("================================================================================")
    # Simulazione Fase di Appoggio (Stance Phase): Alta flessione, torsione minima causata dal carico simmetrico
    print("   SIMULATION: ROBOTIC GAIT STEP - STANCE PHASE (HIGH LOAD)")
    print("================================================================================")
    stance_telemetry = engine.process_gait_telemetry(shift_plus_45_pm=2450.0, shift_minus_45_pm=2410.0)
    print(json.dumps(stance_telemetry, indent=4))
    
    print("\n================================================================================")
    # Simulazione Fase di Oscillazione (Swing Phase) con rotazione: Flessione dinamica e torsione asimmetrica
    print("   SIMULATION: ROBOTIC GAIT STEP - SWING PHASE WITH LATERAL TORQUE")
    print("================================================================================")
    swing_telemetry = engine.process_gait_telemetry(shift_plus_45_pm=1200.0, shift_minus_45_pm=850.0)
    print(json.dumps(swing_telemetry, indent=4))
    print("================================================================================")
