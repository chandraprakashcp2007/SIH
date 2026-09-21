/**
 * Real-Time WebSocket Client for PRAHARI Command Centre
 */
import { audioAlertManager } from './audioAlerts';

type Listener = (data: any) => void;

class WebSocketClient {
  private ws: WebSocket | null = null;
  private listeners: Map<string, Set<Listener>> = new Map();
  private reconnectInterval = 2000;
  private isConnected = false;

  constructor() {
    this.connect();
  }

  public connect() {
    if (typeof window === 'undefined') return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const token = localStorage.getItem('prahari_token');
    if (!token) return;
    const wsUrl = `${protocol}//${host}/ws/live`;

    try {
      // Keep bearer material out of URLs, access logs, history, and proxy traces.
      this.ws = new WebSocket(wsUrl, ['prahari', token]);

      this.ws.onopen = () => {
        this.isConnected = true;
        this.dispatch('connection.status', { connected: true });
      };

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          const type = message.type;
          const data = message.data;

          // Sound alarm on new or updated alerts
          if (type === 'alert.created' || type === 'alert.updated') {
            if (data.severity === 'CRITICAL' || data.severity === 'WARNING') {
              audioAlertManager.triggerIncidentAlarm(data.severity, data.hazard);
            }
          }

          this.dispatch(type, data);
        } catch (err) {
          console.warn('Error parsing WebSocket frame:', err);
        }
      };

      this.ws.onclose = () => {
        this.isConnected = false;
        this.dispatch('connection.status', { connected: false });
        setTimeout(() => this.connect(), this.reconnectInterval);
      };

      this.ws.onerror = (err) => {
        console.warn('WebSocket error, reconnecting...', err);
        this.ws?.close();
      };
    } catch (e) {
      setTimeout(() => this.connect(), this.reconnectInterval);
    }
  }

  public subscribe(eventType: string, callback: Listener): () => void {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set());
    }
    this.listeners.get(eventType)!.add(callback);

    // Return cleanup unsubscribe function
    return () => {
      this.listeners.get(eventType)?.delete(callback);
    };
  }

  public dispatch(eventType: string, data: any) {
    const subs = this.listeners.get(eventType);
    if (subs) {
      subs.forEach((cb) => {
        try {
          cb(data);
        } catch (err) {
          console.error(`Error in subscriber for ${eventType}:`, err);
        }
      });
    }
  }

  public getIsConnected(): boolean {
    return this.isConnected;
  }
}

export const wsClient = new WebSocketClient();
