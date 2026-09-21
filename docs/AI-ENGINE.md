# PRAHARI-NET Hybrid AI & Multi-Sensor Fusion Engine

**Location:** `backend/app/ai/`  
**Philosophy:** Transparent, explainable, trust-weighted physical fusion combining unsupervised anomaly detection with deterministic domain rules.

---

## 1. Multi-Sensor Fusion Formulations

### 1.1 JALA-01 Flood Assessment
$$
R_{\text{JALA}} = 0.40 \cdot \overline{WL} \cdot T_{\text{WL}} + 0.30 \cdot V_{\text{rise}} \cdot T_{\text{WL}} + 0.15 \cdot A_{\text{rise}} \cdot T_{\text{WL}} + 0.15 \cdot P_{\text{rain}} \cdot T_{\text{rain}}
$$
Where:
* $\overline{WL}$ = Normalized water level against critical threshold (180 cm).
* $V_{\text{rise}}$ = First kinematic derivative ($\Delta \text{cm} / \text{min}$).
* $A_{\text{rise}}$ = Second derivative (acceleration $\Delta V / \Delta t$).
* $P_{\text{rain}}$ = Local precipitation intensity (mm/hr).
* $T_{\text{WL}}, T_{\text{rain}}$ = Dynamic sensor trust coefficients ($0.0 \le T \le 1.0$).

### 1.2 AGNI-02 Fire Assessment & Contradiction Suppression
$$
\text{Air}_{\text{idx}} = (0.60 \cdot \text{MQ2}_{\text{norm}} + 0.40 \cdot \text{MQ135}_{\text{norm}}) \cdot \min(T_{\text{MQ2}}, T_{\text{MQ135}})
$$
* **Isolated Smoke Spike Handling:** If MQ-2 spikes $>650$ while temperature $<38^\circ\text{C}$ and optical flame is false, $T_{\text{MQ2}}$ decays to $25\%$. Risk remains in Watch, suppressing false alarms.
* **Corroborated Fire:** If optical flame detects infrared radiation alongside thermal rise $>45^\circ\text{C}$, risk jumps to $\ge 76\%$ (**CRITICAL FIRE**).

### 1.3 BHUMI-03 Landslide & Pore Pressure Assessment
$$
R_{\text{BHUMI}} = 0.35 \cdot S_{\text{soil}} + 0.35 \cdot \Delta\theta_{\text{tilt}} + 0.20 \cdot \text{RMS}_{\text{vib}} + 0.10 \cdot P_{24\text{h}}
$$
* **Failure Condition:** If soil saturation $>70\%$ and inclinometer tilt delta $>2.0^\circ$, geotechnical slope shear is declared (**CRITICAL LANDSLIDE**).

---

## 2. Unsupervised Anomaly Detection
Uses **Scikit-learn `IsolationForest`** initialized on nominal environmental vectors.  
Outputs an `anomaly_score` in $[0.0, 1.0]$, flagging subtle deviations even before threshold crossing.

---

## 3. Explainable AI (XAI) Schema
Every alert outputs both:
1. `human_readable`: Clear causal explanation answering **"WHY?"**.
2. `machine_readable`: Breakdown of mathematical factors, sensor trusts, and timestamps for audit logs.
