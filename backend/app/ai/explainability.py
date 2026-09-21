"""
PRAHARI-NET Explainable AI (XAI) Engine
Generates human-readable 'WHY?' narratives and structured machine-readable factor breakdowns.
"""
from typing import Dict, Any, List


class ExplainabilityEngine:
    """Generates dual-format transparency explanations for every automated hazard score."""

    def generate_explanation(
        self,
        node_id: str,
        risk_score: float,
        risk_band: str,
        confidence: float,
        factors: List[Dict[str, Any]],
        trust: Dict[str, float],
        anomalies: List[str]
    ) -> Dict[str, Any]:
        """
        Produce:
        {
          "human_readable": str,
          "machine_readable": dict,
          "recommended_action": str
        }
        """
        reasons: List[str] = []

        if node_id == "JALA-01":
            action = self._action_jala(risk_band)
            reasons = self._explain_jala(factors, anomalies)
        elif node_id == "AGNI-02":
            action = self._action_agni(risk_band)
            reasons = self._explain_agni(factors, anomalies)
        elif node_id == "BHUMI-03":
            action = self._action_bhumi(risk_band)
            reasons = self._explain_bhumi(factors, anomalies)
        else:
            action = "Monitor node telemetry."
            reasons = ["Telemetry is within baseline observation window."]

        # Build formatted human narrative
        lines = [
            f"ASSESSMENT: {risk_band} ({risk_score:.0f}%)",
            "",
            "WHY?",
        ]
        for r in reasons:
            lines.append(f"• {r}")

        if anomalies:
            lines.append("")
            lines.append("DATA QUALITY / TRUST FLAGS:")
            for a in anomalies:
                lines.append(f"⚠ {a}")

        lines.append("")
        lines.append(f"CONFIDENCE: {confidence:.0f}%")
        lines.append(f"RECOMMENDED PROTOTYPE ACTION: {action}")

        human_text = "\n".join(lines)

        machine_json = {
            "node_id": node_id,
            "risk_band": risk_band,
            "risk_score": risk_score,
            "confidence": confidence,
            "contributing_factors": factors,
            "sensor_trust": trust,
            "anomaly_flags": anomalies,
            "bullet_reasons": reasons,
            "recommended_action": action
        }

        return {
            "human_readable": human_text,
            "machine_readable": machine_json,
            "recommended_action": action
        }

    def _explain_jala(self, factors: List[Dict[str, Any]], anomalies: List[str]) -> List[str]:
        reasons = []
        for f in factors:
            name = f["factor"]
            val = f["value"]
            score = f.get("score", 0.0)
            if "Level" in name and score > 40:
                reasons.append(f"Water gauge reading is elevated at {val}.")
            elif "Rate of Rise" in name and score > 30:
                reasons.append(f"Rate of rise increased rapidly to {val}.")
            elif "Acceleration" in name and score > 30:
                reasons.append(f"Positive flood surge acceleration detected ({val}).")
            elif "Rainfall" in name and score > 25:
                reasons.append(f"Local catchment precipitation rate is elevated at {val}.")
        
        if not reasons:
            reasons.append("River water levels and precipitation conform to normal hydrological baseline.")
        return reasons

    def _explain_agni(self, factors: List[Dict[str, Any]], anomalies: List[str]) -> List[str]:
        reasons = []
        for f in factors:
            name = f["factor"]
            val = f["value"]
            score = f.get("score", 0.0)
            if "Gas" in name and score > 40:
                reasons.append(f"Combustion gas / smoke particulate concentration detected ({val}).")
            elif "Thermal" in name and score > 30:
                reasons.append(f"Ambient thermal reading elevated at {val}.")
            elif "Flame" in name and "DETECTED" in str(val):
                reasons.append("Active optical IR/flame radiation signature confirmed.")
            elif "Vision" in name and score > 35:
                reasons.append(f"Visual AI detector reported {val} confidence of flame/smoke plume.")

        if not reasons:
            reasons.append("Air quality, infrared radiation, and temperature match ambient environmental baseline.")
        return reasons

    def _explain_bhumi(self, factors: List[Dict[str, Any]], anomalies: List[str]) -> List[str]:
        reasons = []
        for f in factors:
            name = f["factor"]
            val = f["value"]
            score = f.get("score", 0.0)
            if "Moisture" in name and score > 40:
                reasons.append(f"Sub-surface soil moisture indicates high pore-pressure saturation ({val}).")
            elif "Tilt" in name and score > 30:
                reasons.append(f"Inclinometer detected structural slope displacement of {val}.")
            elif "Vibration" in name and score > 25:
                reasons.append(f"Sub-surface acoustic micro-tremors measured at {val}.")
            elif "Precipitation" in name and score > 30:
                reasons.append(f"Cumulative antecedent rainfall reached {val}.")

        if not reasons:
            reasons.append("Slope inclination, geophone vibrations, and soil moisture remain in stable geological equilibrium.")
        return reasons

    def _action_jala(self, band: str) -> str:
        if band == "CRITICAL":
            return "Sound audible flood siren; initiate riverbank evacuation and notify NDRF/SDMA emergency dispatch."
        elif band == "WARNING":
            return "Deploy field observation team, inspect culverts/sluice gates, and prepare upstream warning sirens."
        elif band == "WATCH":
            return "Monitor upstream catchment telemetry and review hourly precipitation radar."
        return "Normal routine hydrological surveillance."

    def _action_agni(self, band: str) -> str:
        if band == "CRITICAL":
            return "Dispatch forest/fire control response team to coordinates immediately; alert nearby residential perimeters."
        elif band == "WARNING":
            return "Request visual drone or optical PTZ camera sweep; confirm thermal anomaly coordinates."
        elif band == "WATCH":
            return "Monitor air quality indexes and check correlation with nearby agricultural stubble or controlled burning."
        return "Normal atmospheric monitoring."

    def _action_bhumi(self, band: str) -> str:
        if band == "CRITICAL":
            return "Trigger local road closure; sound slope siren and evacuate downstream transit corridor immediately."
        elif band == "WARNING":
            return "Issue slow-speed transit advisory for hillside road; inspect drainage channels and slope retaining walls."
        elif band == "WATCH":
            return "Track cumulative soil moisture and inclinometer drift rates after heavy rainfall."
        return "Normal geotechnical slope stability."


explainability_engine = ExplainabilityEngine()
