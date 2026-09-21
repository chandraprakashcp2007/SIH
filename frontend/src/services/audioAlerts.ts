/**
 * PRAHARI-NET Acoustic Alert Synthesizer
 * Uses Web Audio API for deterministic zero-dependency acoustic siren synthesis.
 * Respects browser autoplay policies with explicit operator opt-in.
 */

class AudioAlertManager {
  private ctx: AudioContext | null = null;
  private isEnabled: boolean = false;
  private isMuted: boolean = false;
  private activeOscillators: OscillatorNode[] = [];

  constructor() {
    // Check saved operator preference
    const saved = localStorage.getItem('prahari_audio_enabled');
    this.isEnabled = saved === 'true';
  }

  public init() {
    if (!this.ctx && typeof window !== 'undefined') {
      const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
      if (AudioContextClass) {
        this.ctx = new AudioContextClass();
      }
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  public setEnabled(enabled: boolean) {
    this.isEnabled = enabled;
    localStorage.setItem('prahari_audio_enabled', enabled ? 'true' : 'false');
    if (enabled) {
      this.init();
      this.playMaintenanceBeep(); // Short confirmation chime
    } else {
      this.stopAll();
    }
  }

  public getEnabled(): boolean {
    return this.isEnabled;
  }

  public setMuted(muted: boolean) {
    this.isMuted = muted;
    if (muted) {
      this.stopAll();
    }
  }

  public getMuted(): boolean {
    return this.isMuted;
  }

  private stopAll() {
    this.activeOscillators.forEach((osc) => {
      try {
        osc.stop();
        osc.disconnect();
      } catch (e) {}
    });
    this.activeOscillators = [];
  }

  private playTone(freq: number, durationSec: number, delaySec: number = 0, type: OscillatorType = 'sine', gainVal: number = 0.2) {
    if (!this.isEnabled || this.isMuted || !this.ctx) return;

    try {
      const now = this.ctx.currentTime + delaySec;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = type;
      osc.frequency.setValueAtTime(freq, now);

      gain.gain.setValueAtTime(0.001, now);
      gain.gain.exponentialRampToValueAtTime(gainVal, now + 0.02);
      gain.gain.setValueAtTime(gainVal, now + durationSec - 0.02);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + durationSec);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start(now);
      osc.stop(now + durationSec);
      this.activeOscillators.push(osc);

      setTimeout(() => {
        const idx = this.activeOscillators.indexOf(osc);
        if (idx !== -1) this.activeOscillators.splice(idx, 1);
      }, (delaySec + durationSec + 0.1) * 1000);
    } catch (e) {
      console.warn('Audio tone synthesis error:', e);
    }
  }

  /**
   * WATCH: 3 short beeps (880 Hz)
   */
  public playWatchAlert() {
    this.init();
    this.stopAll();
    this.playTone(880, 0.12, 0.0);
    this.playTone(880, 0.12, 0.22);
    this.playTone(880, 0.12, 0.44);
  }

  /**
   * WARNING: Repeated moderate beeps (660 Hz)
   */
  public playWarningAlert() {
    this.init();
    this.stopAll();
    this.playTone(660, 0.25, 0.0, 'triangle', 0.25);
    this.playTone(660, 0.25, 0.35, 'triangle', 0.25);
    this.playTone(660, 0.25, 0.70, 'triangle', 0.25);
  }

  /**
   * CRITICAL FLOOD: Long alternating dual-tone alarm (440 Hz / 880 Hz)
   */
  public playCriticalFloodAlert() {
    this.init();
    this.stopAll();
    this.playTone(440, 0.35, 0.0, 'sawtooth', 0.3);
    this.playTone(880, 0.35, 0.36, 'sawtooth', 0.3);
    this.playTone(440, 0.35, 0.72, 'sawtooth', 0.3);
    this.playTone(880, 0.35, 1.08, 'sawtooth', 0.3);
  }

  /**
   * CRITICAL FIRE: Rapid higher-frequency emergency chirp (1200 Hz - 1500 Hz)
   */
  public playCriticalFireAlert() {
    this.init();
    this.stopAll();
    for (let i = 0; i < 6; i++) {
      this.playTone(1200 + (i % 2) * 300, 0.08, i * 0.12, 'square', 0.2);
    }
  }

  /**
   * CRITICAL LANDSLIDE: Low-frequency deep geological rumble alarm (180 Hz - 240 Hz)
   */
  public playCriticalLandslideAlert() {
    this.init();
    this.stopAll();
    this.playTone(180, 0.5, 0.0, 'sawtooth', 0.35);
    this.playTone(220, 0.5, 0.52, 'sawtooth', 0.35);
    this.playTone(180, 0.6, 1.05, 'sawtooth', 0.35);
  }

  /**
   * MAINTENANCE: 2 low beeps (330 Hz)
   */
  public playMaintenanceBeep() {
    this.init();
    this.playTone(330, 0.15, 0.0, 'sine', 0.15);
    this.playTone(330, 0.15, 0.25, 'sine', 0.15);
  }

  /**
   * Trigger appropriate sound based on severity and hazard.
   */
  public triggerIncidentAlarm(severity: string, hazard: string) {
    if (severity === 'CRITICAL') {
      if (hazard === 'FLOOD') this.playCriticalFloodAlert();
      else if (hazard === 'FIRE') this.playCriticalFireAlert();
      else if (hazard === 'LANDSLIDE') this.playCriticalLandslideAlert();
      else this.playCriticalFloodAlert();
    } else if (severity === 'WARNING') {
      this.playWarningAlert();
    } else if (severity === 'WATCH') {
      this.playWatchAlert();
    }
  }
}

export const audioAlertManager = new AudioAlertManager();
