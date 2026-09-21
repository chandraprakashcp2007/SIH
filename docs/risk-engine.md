# PRAHARI-NET Hybrid Risk Engine & Sensor Fusion Specification

## Mathematical Principles

The Hybrid Risk Engine combines dynamic reliability discounting, physics-based kinematic rules, and unsupervised machine learning:

### 1. Dynamic Sensor Trust Scoring
For each transducer $i$, reliability $T_i \in [0, 100]$ is evaluated against 4 deterministic safety tests:
$$T_i = 100 - \Delta_{\text{bounds}} - \Delta_{\text{stuck}} - \Delta_{\text{jump}} - \Delta_{\text{contradiction}}$$
- **Bounds Test:** Penalizes values beyond physical operating limits (e.g. water level $> 1000\text{ cm}$).
- **Frozen Transducer Test:** Catches analog values exhibiting exactly zero micro-variance across 6 consecutive samples.
- **Kinematic Jump Test:** Penalizes instantaneous delta exceeding maximum physical acceleration rates.
- **Cross-Sensor Contradiction:** Penalizes single isolated sensors that contradict co-located corroborating transducers.

### 2. Multi-Sensor Rule Fusion
The fusion engine computes the raw weighted hazard index:
$$S_{\text{raw}} = \sum_{i=1}^N w_i \cdot \frac{T_i}{100} \cdot f(m_i)$$
Where $w_i$ is sensor criticality weight, $T_i$ is trust score, and $f(m_i)$ is normalized severity.

### 3. Isolation Forest Anomaly Detection
In parallel, an unsupervised `IsolationForest` model (50 estimators, zero GPU requirements) computes a multivariate contamination score $A \in [0, 1.0]$. This catches subtle non-linear multi-sensor patterns without requiring labeled disaster training sets.

### 4. Calibrated Operational Risk Bands
- **NORMAL:** $0.0 - 25.0\%$ (Nominal baseline surveillance)
- **WATCH:** $26.0 - 50.0\%$ (Advisory condition; heightened sampling)
- **WARNING:** $51.0 - 75.0\%$ (Action required; field teams notified)
- **CRITICAL:** $76.0 - 100.0\%$ (Immediate danger; evacuation alarms sounded)
