// src/renderer/managers/RecordingManager.ts

import { RecordingState } from '@shared/types.js';

export interface RecordingConfig {
  sampleRate: number;
  channels: number;
  bitDepth: number;
  format: string;
  maxDuration: number; // seconds
  silenceThreshold: number;
  silenceTimeout: number; // ms
}

export interface RecordingManagerEvents {
  'recording:started': () => void;
  'recording:stopped': () => void;
  'recording:error': (error: Error) => void;
  'recording:data': (audioData: Blob) => void;
  'transcript:received': (transcript: string) => void;
  'transcript:error': (error: Error) => void;
  'volume:change': (volume: number) => void;
}

export class RecordingManager {
  private static instance: RecordingManager;
  
  // Recording state
  private state: RecordingState = RecordingState.IDLE;
  private mediaRecorder: MediaRecorder | null = null;
  private audioStream: MediaStream | null = null;
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  
  // Recording data
  private audioChunks: Blob[] = [];
  private recordingStartTime: number = 0;
  private recordingTimer: NodeJS.Timeout | null = null;
  private silenceTimer: NodeJS.Timeout | null = null;
  
  // Configuration
  private config: RecordingConfig = {
    sampleRate: 44100,
    channels: 1,
    bitDepth: 16,
    format: 'audio/webm;codecs=opus',
    maxDuration: 300, // 5 minutes
    silenceThreshold: 0.01,
    silenceTimeout: 3000 // 3 seconds
  };

  // Event callbacks
  private eventCallbacks: Map<keyof RecordingManagerEvents, Function[]> = new Map();
  
  // Volume monitoring
  private volumeMonitoringActive = false;
  private volumeAnimationFrame: number | null = null;

  private constructor() {
    this.checkBrowserSupport();
  }

  public static getInstance(): RecordingManager {
    if (!RecordingManager.instance) {
      RecordingManager.instance = new RecordingManager();
    }
    return RecordingManager.instance;
  }

  // =============================================================================
  // INITIALIZATION
  // =============================================================================

  public async initialize(): Promise<void> {
    try {
      console.log('🎤 Initializing RecordingManager...');
      
      await this.checkPermissions();
      await this.loadConfiguration();
      
      console.log('✅ RecordingManager initialized');
    } catch (error) {
      console.error('❌ Failed to initialize RecordingManager:', error);
      throw error;
    }
  }

  private checkBrowserSupport(): void {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      throw new Error('Media recording not supported in this browser');
    }

    if (!window.MediaRecorder) {
      throw new Error('MediaRecorder API not supported');
    }

    if (!window.AudioContext && !window.webkitAudioContext) {
      throw new Error('Web Audio API not supported');
    }
  }

  private async checkPermissions(): Promise<void> {
    try {
      const permissionStatus = await navigator.permissions.query({ name: 'microphone' as PermissionName });
      
      if (permissionStatus.state === 'denied') {
        throw new Error('Microphone permission denied');
      }

      console.log('🎤 Microphone permission:', permissionStatus.state);
    } catch (error) {
      console.warn('Could not check microphone permissions:', error);
    }
  }

  private async loadConfiguration(): Promise<void> {
    try {
      if (window.electronAPI) {
        const config = await window.electronAPI.loadConfig();
        if (config?.stt) {
          this.updateConfiguration(config.stt);
        }
      }
    } catch (error) {
      console.warn('Failed to load recording configuration:', error);
    }
  }

  private updateConfiguration(sttConfig: any): void {
    if (sttConfig.timeout) {
      this.config.maxDuration = sttConfig.timeout / 1000;
    }
    // Add other STT config mappings as needed
  }

  // =============================================================================
  // RECORDING CONTROL
  // =============================================================================

  public async startRecording(): Promise<void> {
    if (this.state !== RecordingState.IDLE) {
      console.warn('Recording already in progress');
      return;
    }

    try {
      console.log('🎤 Starting recording...');
      this.setState(RecordingState.RECORDING);
      
      // Get audio stream
      await this.initializeAudioStream();
      
      // Set up audio analysis
      this.setupAudioAnalysis();
      
      // Initialize MediaRecorder
      this.initializeMediaRecorder();
      
      // Start recording
      this.mediaRecorder!.start(100); // Collect data every 100ms
      this.recordingStartTime = Date.now();
      
      // Set up timers
      this.startRecordingTimer();
      this.startVolumeMonitoring();
      
      this.emit('recording:started');
      console.log('✅ Recording started');
    } catch (error) {
      console.error('❌ Failed to start recording:', error);
      this.setState(RecordingState.IDLE);
      this.emit('recording:error', error as Error);
      throw error;
    }
  }

  public async stopRecording(): Promise<string | null> {
    if (this.state !== RecordingState.RECORDING) {
      console.warn('No recording in progress');
      return null;
    }

    try {
      console.log('🛑 Stopping recording...');
      this.setState(RecordingState.PROCESSING);
      
      // Stop media recorder
      if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
        this.mediaRecorder.stop();
      }
      
      // Clean up timers and monitoring
      this.stopRecordingTimer();
      this.stopVolumeMonitoring();
      this.stopSilenceTimer();
      
      // Wait for final audio data
      const audioBlob = await this.finalizeRecording();
      
      // Process with STT
      const transcript = await this.processAudioWithSTT(audioBlob);
      
      this.setState(RecordingState.IDLE);
      this.emit('recording:stopped');
      
      return transcript;
    } catch (error) {
      console.error('❌ Failed to stop recording:', error);
      this.setState(RecordingState.IDLE);
      this.emit('recording:error', error as Error);
      return null;
    }
  }

  public cancelRecording(): void {
    if (this.state === RecordingState.IDLE) {
      return;
    }

    console.log('❌ Cancelling recording...');
    
    // Stop everything without processing
    if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
      this.mediaRecorder.stop();
    }
    
    this.cleanup();
    this.setState(RecordingState.IDLE);
    
    console.log('✅ Recording cancelled');
  }

  // =============================================================================
  // AUDIO STREAM MANAGEMENT
  // =============================================================================

  private async initializeAudioStream(): Promise<void> {
    try {
      this.audioStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: this.config.sampleRate,
          channelCount: this.config.channels,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });
    } catch (error) {
      if (error instanceof Error) {
        if (error.name === 'NotAllowedError') {
          throw new Error('Microphone permission denied. Please allow microphone access.');
        } else if (error.name === 'NotFoundError') {
          throw new Error('No microphone found. Please connect a microphone.');
        } else if (error.name === 'NotReadableError') {
          throw new Error('Microphone is already in use by another application.');
        }
      }
      throw new Error('Failed to access microphone: ' + error);
    }
  }

  private setupAudioAnalysis(): void {
    if (!this.audioStream) return;

    try {
      // Create audio context
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      this.audioContext = new AudioContextClass();
      
      // Create analyser node
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 256;
      this.analyser.smoothingTimeConstant = 0.8;
      
      // Connect audio stream to analyser
      const source = this.audioContext.createMediaStreamSource(this.audioStream);
      source.connect(this.analyser);
      
      console.log('🔊 Audio analysis setup complete');
    } catch (error) {
      console.warn('Failed to setup audio analysis:', error);
    }
  }

  private initializeMediaRecorder(): void {
    if (!this.audioStream) {
      throw new Error('Audio stream not initialized');
    }

    try {
      // Determine the best format to use
      const mimeType = this.getBestMimeType();
      
      this.mediaRecorder = new MediaRecorder(this.audioStream, {
        mimeType: mimeType
      });

      // Set up event handlers
      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          this.audioChunks.push(event.data);
          this.emit('recording:data', event.data);
        }
      };

      this.mediaRecorder.onstop = () => {
        console.log('📼 MediaRecorder stopped');
      };

      this.mediaRecorder.onerror = (event) => {
        console.error('❌ MediaRecorder error:', event);
        this.emit('recording:error', new Error('Recording failed'));
      };

      console.log('📼 MediaRecorder initialized with format:', mimeType);
    } catch (error) {
      throw new Error('Failed to initialize MediaRecorder: ' + error);
    }
  }

  private getBestMimeType(): string {
    const preferredTypes = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/ogg;codecs=opus',
      'audio/mp4',
      'audio/wav'
    ];

    for (const type of preferredTypes) {
      if (MediaRecorder.isTypeSupported(type)) {
        return type;
      }
    }

    throw new Error('No supported audio format found');
  }

  // =============================================================================
  // VOLUME MONITORING & SILENCE DETECTION
  // =============================================================================

  private startVolumeMonitoring(): void {
    this.volumeMonitoringActive = true;
    this.monitorVolume();
  }

  private stopVolumeMonitoring(): void {
    this.volumeMonitoringActive = false;
    if (this.volumeAnimationFrame) {
      cancelAnimationFrame(this.volumeAnimationFrame);
      this.volumeAnimationFrame = null;
    }
  }

  private monitorVolume(): void {
    if (!this.volumeMonitoringActive || !this.analyser) {
      return;
    }

    const bufferLength = this.analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    
    this.analyser.getByteFrequencyData(dataArray);
    
    // Calculate volume level (0-1)
    let sum = 0;
    for (const value of dataArray) {
      sum += value;
    }
    const volume = sum / (bufferLength * 255);
    
    this.emit('volume:change', volume);
    
    // Check for silence
    this.checkSilence(volume);
    
    // Continue monitoring
    this.volumeAnimationFrame = requestAnimationFrame(() => this.monitorVolume());
  }

  private checkSilence(volume: number): void {
    if (volume < this.config.silenceThreshold) {
      // Start silence timer if not already started
      if (!this.silenceTimer) {
        this.silenceTimer = setTimeout(() => {
          console.log('🔇 Silence detected, auto-stopping recording');
          this.stopRecording();
        }, this.config.silenceTimeout);
      }
    } else {
      // Cancel silence timer if volume detected
      this.stopSilenceTimer();
    }
  }

  private stopSilenceTimer(): void {
    if (this.silenceTimer) {
      clearTimeout(this.silenceTimer);
      this.silenceTimer = null;
    }
  }

  // =============================================================================
  // RECORDING TIMERS
  // =============================================================================

  private startRecordingTimer(): void {
    this.recordingTimer = setTimeout(() => {
      console.log('⏰ Max recording duration reached, auto-stopping');
      this.stopRecording();
    }, this.config.maxDuration * 1000);
  }

  private stopRecordingTimer(): void {
    if (this.recordingTimer) {
      clearTimeout(this.recordingTimer);
      this.recordingTimer = null;
    }
  }

  // =============================================================================
  // AUDIO PROCESSING
  // =============================================================================

  private async finalizeRecording(): Promise<Blob> {
    return new Promise((resolve, reject) => {
      if (this.audioChunks.length === 0) {
        reject(new Error('No audio data recorded'));
        return;
      }

      try {
        const mimeType = this.mediaRecorder?.mimeType || 'audio/webm';
        const audioBlob = new Blob(this.audioChunks, { type: mimeType });
        
        // Clear chunks for next recording
        this.audioChunks = [];
        
        console.log('📼 Audio finalized:', {
          size: `${(audioBlob.size / 1024).toFixed(2)} KB`,
          duration: `${((Date.now() - this.recordingStartTime) / 1000).toFixed(2)}s`,
          type: mimeType
        });
        
        resolve(audioBlob);
      } catch (error) {
        reject(error);
      }
    });
  }

  private async processAudioWithSTT(audioBlob: Blob): Promise<string | null> {
    try {
      console.log('🤖 Processing audio with Speech-to-Text...');
      
      // Load STT configuration
      const config = await window.electronAPI?.loadConfig();
      if (!config?.stt?.enabled) {
        console.log('STT is disabled, skipping transcription');
        return null;
      }

      // Convert audio to format suitable for STT API
      const audioFile = await this.convertAudioForSTT(audioBlob);
      
      // Send to STT service
      const transcript = await this.sendToSTTService(audioFile, config.stt);
      
      if (transcript) {
        this.emit('transcript:received', transcript);
        console.log('✅ Transcript received:', transcript);
      }
      
      return transcript;
    } catch (error) {
      console.error('❌ STT processing failed:', error);
      this.emit('transcript:error', error as Error);
      return null;
    }
  }

  private async convertAudioForSTT(audioBlob: Blob): Promise<File> {
    // Convert to a format suitable for STT APIs (usually wav or mp3)
    // For now, we'll return the blob as a File object
    // In a real implementation, you might want to convert to WAV
    
    const file = new File([audioBlob], 'recording.webm', {
      type: audioBlob.type,
      lastModified: Date.now()
    });
    
    return file;
  }

  private async sendToSTTService(audioFile: File, sttConfig: any): Promise<string | null> {
    try {
      // Create FormData for file upload
      const formData = new FormData();
      formData.append('file', audioFile);
      formData.append('model', sttConfig.model || 'whisper-1');
      
      // Make request to STT API
      const response = await fetch(`${sttConfig.apiBase}/audio/transcriptions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${sttConfig.apiKey || ''}`,
        },
        body: formData
      });

      if (!response.ok) {
        throw new Error(`STT API error: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      return result.text || null;
    } catch (error) {
      console.error('STT API request failed:', error);
      throw error;
    }
  }

  // =============================================================================
  // STATE MANAGEMENT
  // =============================================================================

  private setState(newState: RecordingState): void {
    const oldState = this.state;
    this.state = newState;
    
    console.log(`🎤 Recording state: ${oldState} → ${newState}`);
  }

  public getState(): RecordingState {
    return this.state;
  }

  public isRecording(): boolean {
    return this.state === RecordingState.RECORDING;
  }

  public isProcessing(): boolean {
    return this.state === RecordingState.PROCESSING;
  }

  public getRecordingDuration(): number {
    if (this.state !== RecordingState.RECORDING) {
      return 0;
    }
    return (Date.now() - this.recordingStartTime) / 1000;
  }

  // =============================================================================
  // EVENT SYSTEM
  // =============================================================================

  public on<K extends keyof RecordingManagerEvents>(
    event: K,
    callback: RecordingManagerEvents[K]
  ): void {
    if (!this.eventCallbacks.has(event)) {
      this.eventCallbacks.set(event, []);
    }
    this.eventCallbacks.get(event)!.push(callback as Function);
  }

  public off<K extends keyof RecordingManagerEvents>(
    event: K,
    callback: RecordingManagerEvents[K]
  ): void {
    const callbacks = this.eventCallbacks.get(event);
    if (callbacks) {
      const index = callbacks.indexOf(callback as Function);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  private emit<K extends keyof RecordingManagerEvents>(
    event: K,
    ...args: Parameters<RecordingManagerEvents[K]>
  ): void {
    const callbacks = this.eventCallbacks.get(event);
    if (callbacks) {
      callbacks.forEach(callback => {
        try {
          callback(...args);
        } catch (error) {
          console.error(`Error in recording event callback for ${event}:`, error);
        }
      });
    }
  }

  // =============================================================================
  // CONFIGURATION
  // =============================================================================

  public updateConfig(newConfig: Partial<RecordingConfig>): void {
    this.config = { ...this.config, ...newConfig };
    console.log('🔧 Recording configuration updated:', this.config);
  }

  public getConfig(): Readonly<RecordingConfig> {
    return { ...this.config };
  }

  // =============================================================================
  // CLEANUP
  // =============================================================================

  private cleanup(): void {
    // Stop timers
    this.stopRecordingTimer();
    this.stopSilenceTimer();
    this.stopVolumeMonitoring();
    
    // Clean up media
    if (this.audioStream) {
      this.audioStream.getTracks().forEach(track => track.stop());
      this.audioStream = null;
    }
    
    if (this.audioContext && this.audioContext.state !== 'closed') {
      this.audioContext.close();
      this.audioContext = null;
    }
    
    this.analyser = null;
    this.mediaRecorder = null;
    
    // Clear audio data
    this.audioChunks = [];
  }

  public destroy(): void {
    console.log('🧹 Destroying RecordingManager...');
    
    // Cancel any ongoing recording
    if (this.state !== RecordingState.IDLE) {
      this.cancelRecording();
    }
    
    // Clean up resources
    this.cleanup();
    
    // Clear event callbacks
    this.eventCallbacks.clear();
    
    console.log('✅ RecordingManager destroyed');
  }

  // =============================================================================
  // UTILITY METHODS
  // =============================================================================

  public static async checkMicrophoneSupport(): Promise<boolean> {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      return devices.some(device => device.kind === 'audioinput');
    } catch {
      return false;
    }
  }

  public static async getMicrophoneDevices(): Promise<MediaDeviceInfo[]> {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      return devices.filter(device => device.kind === 'audioinput');
    } catch {
      return [];
    }
  }

  public getRecordingStats(): {
    state: RecordingState;
    duration: number;
    dataSize: number;
    isSupported: boolean;
  } {
    return {
      state: this.state,
      duration: this.getRecordingDuration(),
      dataSize: this.audioChunks.reduce((size, chunk) => size + chunk.size, 0),
      isSupported: 'mediaDevices' in navigator && 'MediaRecorder' in window
    };
  }
}

// Global type declarations for WebKit browsers
declare global {
  interface Window {
    webkitAudioContext: typeof AudioContext;
  }
}