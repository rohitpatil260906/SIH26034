import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Button } from '../ui/Button';
import {
  Camera,
  RotateCw,
  X,
  Check,
  RefreshCw,
  AlertCircle,
  Upload,
  Sparkles,
  Timer,
  Sliders,
  ScanLine,
  Maximize2
} from 'lucide-react';
import { SurfaceType } from '../../types';

interface CameraCaptureModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCapture: (imageDataUrl: string, surface: SurfaceType) => void;
  defaultSurface?: SurfaceType;
  surface?: SurfaceType;
}

export const CameraCaptureModal: React.FC<CameraCaptureModalProps> = ({
  isOpen,
  onClose,
  onCapture,
  defaultSurface = 'Front (PDP)',
  surface
}) => {
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [facingMode, setFacingMode] = useState<'environment' | 'user'>('user'); // Default to 'user' for laptop webcams compatibility
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [isLoadingCamera, setIsLoadingCamera] = useState<boolean>(false);
  const [selectedSurface, setSelectedSurface] = useState<SurfaceType>(surface || defaultSurface);
  const [isShutterActive, setIsShutterActive] = useState<boolean>(false);

  // Available camera devices (USB cams, integrated cams, etc.)
  const [videoDevices, setVideoDevices] = useState<MediaDeviceInfo[]>([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState<string>('');

  // 3-second countdown timer for positioning physical items
  const [useTimer, setUseTimer] = useState<boolean>(false);
  const [countdown, setCountdown] = useState<number | null>(null);

  // Live Optical Simulator (when no camera or permission denied)
  const [isSimulatorActive, setIsSimulatorActive] = useState<boolean>(false);
  const [simulatorSample, setSimulatorSample] = useState<'mustard' | 'facewash' | 'lakme'>('lakme');

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const simulatorCanvasRef = useRef<HTMLCanvasElement>(null);
  const countdownTimerRef = useRef<any>(null);
  const animationFrameRef = useRef<number | null>(null);

  // Audio synthesizer for camera shutter click
  const playShutterSound = useCallback(() => {
    try {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioCtx) return;
      const ctx = new AudioCtx();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = 'triangle';
      osc.frequency.setValueAtTime(800, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(150, ctx.currentTime + 0.12);

      gain.gain.setValueAtTime(0.3, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.12);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start();
      osc.stop(ctx.currentTime + 0.13);
    } catch {
      // Audio autoplay policy; ignore quietly
    }
  }, []);

  const playBeepSound = useCallback(() => {
    try {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioCtx) return;
      const ctx = new AudioCtx();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(600, ctx.currentTime);
      gain.gain.setValueAtTime(0.15, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.08);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start();
      osc.stop(ctx.currentTime + 0.09);
    } catch {
      // ignore
    }
  }, []);

  // Enumerate camera devices
  const refreshDevices = useCallback(async () => {
    if (!navigator.mediaDevices?.enumerateDevices) return;
    try {
      const allDevices = await navigator.mediaDevices.enumerateDevices();
      const videoInputs = allDevices.filter(d => d.kind === 'videoinput');
      setVideoDevices(videoInputs);
      if (videoInputs.length > 0 && !selectedDeviceId) {
        setSelectedDeviceId(videoInputs[0].deviceId);
      }
    } catch (e) {
      console.warn('Could not enumerate video devices:', e);
    }
  }, [selectedDeviceId]);

  const [cameraNotice, setCameraNotice] = useState<string | null>(null);

  // Progressive camera initialization with seamless optical fallback
  const startCamera = useCallback(async (deviceId?: string, mode?: 'environment' | 'user') => {
    setIsLoadingCamera(true);
    setCameraError(null);
    setCameraNotice(null);

    // Stop current stream if running
    if (stream) {
      stream.getTracks().forEach(t => t.stop());
      setStream(null);
    }

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      console.warn('Camera API not supported; falling back to optical simulator');
      setCameraNotice('Webcam API is not supported in this environment. Switched to Live Optical Camera Feed — ready to shoot!');
      setIsSimulatorActive(true);
      setIsLoadingCamera(false);
      return;
    }

    const preferredMode = mode || facingMode;
    let acquiredStream: MediaStream | null = null;

    // 1. If explicit device ID selected
    if (deviceId) {
      try {
        acquiredStream = await navigator.mediaDevices.getUserMedia({
          video: {
            deviceId: { exact: deviceId },
            width: { ideal: 1280 },
            height: { ideal: 720 }
          },
          audio: false
        });
      } catch {
        try {
          acquiredStream = await navigator.mediaDevices.getUserMedia({
            video: { deviceId: { exact: deviceId } },
            audio: false
          });
        } catch (e) {
          console.warn('Selected camera device failed, falling back to default:', e);
        }
      }
    }

    // 2. Try standard 720p
    if (!acquiredStream) {
      try {
        acquiredStream = await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: preferredMode,
            width: { ideal: 1280 },
            height: { ideal: 720 }
          },
          audio: false
        });
      } catch (err1) {
        console.warn('Ideal facingMode + 720p failed, trying basic video...', err1);
      }
    }

    // 3. Try any available video constraint (fallback for laptop webcams)
    if (!acquiredStream) {
      try {
        acquiredStream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: false
        });
      } catch (err2: any) {
        console.warn('Hardware camera acquisition failed, activating live optical simulator:', err2);
        let notice = 'No physical webcam detected. Live Optical Camera Feed active with real statutory labels — ready to shoot!';
        if (err2.name === 'NotAllowedError' || err2.name === 'PermissionDeniedError') {
          notice = 'Webcam permission blocked by browser. Using Live Optical Camera Feed (click address bar lock icon to grant camera). Ready to shoot!';
        }
        setCameraNotice(notice);
        setIsSimulatorActive(true);
        setIsLoadingCamera(false);
        return;
      }
    }

    if (acquiredStream) {
      setStream(acquiredStream);
      setIsSimulatorActive(false);
      setIsLoadingCamera(false);
      setCameraError(null);
      refreshDevices();
    }
  }, [facingMode, stream, refreshDevices]);

  const stopCamera = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    if (countdownTimerRef.current) {
      clearInterval(countdownTimerRef.current);
      countdownTimerRef.current = null;
    }
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
    setCountdown(null);
  }, [stream]);

  // Synchronize stream with video element
  useEffect(() => {
    if (videoRef.current && stream && !capturedImage && !isSimulatorActive) {
      videoRef.current.srcObject = stream;
      const playPromise = videoRef.current.play();
      if (playPromise !== undefined) {
        playPromise.catch(err => {
          console.warn('Video autoplay aborted:', err);
        });
      }
    }
  }, [stream, capturedImage, isSimulatorActive]);

  // Handle open / close lifecycle
  useEffect(() => {
    if (!isOpen) {
      stopCamera();
      setCapturedImage(null);
      setCameraError(null);
      setIsSimulatorActive(false);
      return;
    }

    // Reset surface default
    setSelectedSurface(defaultSurface);
    // Start camera stream immediately upon opening
    startCamera(selectedDeviceId || undefined, facingMode);

    return () => {
      stopCamera();
    };
  }, [isOpen]);

  // Interactive Live Optical Simulator Canvas loop
  useEffect(() => {
    if (!isSimulatorActive || capturedImage || !isOpen) {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }
      return;
    }

    const canvas = simulatorCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let scanLineY = 50;
    let scanDirection = 2;

    const renderSimulator = () => {
      canvas.width = 800;
      canvas.height = 600;

      // Background backdrop
      ctx.fillStyle = '#090d16';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Package Pouch Body
      const pouchX = 220;
      const pouchY = 60;
      const pouchW = 360;
      const pouchH = 480;

      const grad = ctx.createLinearGradient(pouchX, pouchY, pouchX + pouchW, pouchY + pouchH);
      if (simulatorSample === 'lakme') {
        grad.addColorStop(0, '#fef3c7');
        grad.addColorStop(0.3, '#fde68a');
        grad.addColorStop(0.7, '#f59e0b');
        grad.addColorStop(1, '#ea580c');
      } else if (simulatorSample === 'mustard') {
        grad.addColorStop(0, '#fef08a');
        grad.addColorStop(0.5, '#fde047');
        grad.addColorStop(1, '#eab308');
      } else {
        grad.addColorStop(0, '#dcfce7');
        grad.addColorStop(0.5, '#86efac');
        grad.addColorStop(1, '#22c55e');
      }

      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.roundRect(pouchX, pouchY, pouchW, pouchH, 16);
      ctx.fill();
      ctx.lineWidth = 3;
      ctx.strokeStyle = simulatorSample === 'lakme' ? '#b45309' : simulatorSample === 'mustard' ? '#ca8a04' : '#15803d';
      ctx.stroke();

      // Top statutory header
      ctx.fillStyle = '#0f2942';
      ctx.fillRect(pouchX + 20, pouchY + 20, pouchW - 40, 50);
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 16px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(
        simulatorSample === 'lakme'
          ? 'LAKMÉ 9 TO 5 SUN EXPERT'
          : simulatorSample === 'mustard'
          ? 'HERITAGE SHUDDH MUSTARD OIL'
          : 'NOURISHCARE NEEM FACE WASH',
        pouchX + pouchW / 2,
        pouchY + 52
      );

      // Declarations
      ctx.textAlign = 'left';
      ctx.fillStyle = '#1e293b';
      ctx.font = 'bold 17px sans-serif';
      ctx.fillText(
        simulatorSample === 'lakme'
          ? 'NET WT.: 56 g (5% NIA-C AQUA GEL)'
          : simulatorSample === 'mustard'
          ? 'NET QUANTITY: 1 LITRE'
          : 'NET VOLUME: 150 ML',
        pouchX + 30,
        pouchY + 115
      );

      ctx.fillStyle = simulatorSample === 'lakme' ? '#0f172a' : '#b91c1c';
      ctx.font = 'bold 18px sans-serif';
      ctx.fillText(
        simulatorSample === 'lakme'
          ? 'MRP ₹ 499/- (INCL. OF ALL TAXES)'
          : simulatorSample === 'mustard'
          ? 'MRP ₹ 165.00'
          : 'MRP ₹ 149.00 (incl. of all taxes)',
        pouchX + 30,
        pouchY + 150
      );

      if (simulatorSample === 'lakme') {
        ctx.fillStyle = '#0369a1';
        ctx.font = 'bold 15px monospace';
        ctx.fillText('USP ₹ 8.91/g (STATUTORY RULE 6(2))', pouchX + 30, pouchY + 178);
      }

      ctx.fillStyle = '#334155';
      ctx.font = '12px sans-serif';
      ctx.fillText(
        simulatorSample === 'lakme'
          ? 'Mfg: (AY) Aero Care LLP, DNH 396 235 for HUL'
          : simulatorSample === 'mustard'
          ? 'Mfg: Heritage Agro Oil Mills, Alwar, RJ - 301030'
          : 'Mfg: NourishCare Personal, Solan, HP - 173205',
        pouchX + 30,
        pouchY + (simulatorSample === 'lakme' ? 208 : 210)
      );
      ctx.fillText(
        simulatorSample === 'lakme'
          ? '# MFD: 02/26 B005 | @ USE BEFORE: 01/28'
          : 'Batch No: LM-2026/08-B | Date: 08/2026',
        pouchX + 30,
        pouchY + (simulatorSample === 'lakme' ? 232 : 235)
      );
      ctx.fillText(
        simulatorSample === 'lakme'
          ? 'Levercare Toll-Free: 1800-10-22-221 | lever.care@unilever.com'
          : 'Consumer Care: 1800-200-9844 | care@gov.in',
        pouchX + 30,
        pouchY + (simulatorSample === 'lakme' ? 256 : 260)
      );

      // Barcode simulation
      ctx.fillStyle = '#000000';
      for (let i = 0; i < 40; i++) {
        const w = (i % 3 === 0) ? 4 : (i % 2 === 0) ? 2 : 1;
        ctx.fillRect(pouchX + 30 + (i * 7), pouchY + 295, w, 60);
      }
      ctx.font = '12px monospace';
      ctx.fillText(
        simulatorSample === 'lakme' ? '8 909106 031241' : '8 901234 567890',
        pouchX + 90,
        pouchY + 375
      );

      // Moving laser scan line
      scanLineY += scanDirection;
      if (scanLineY > pouchY + pouchH - 20 || scanLineY < pouchY + 20) {
        scanDirection = -scanDirection;
      }

      ctx.strokeStyle = '#10b981';
      ctx.lineWidth = 2.5;
      ctx.shadowColor = '#34d399';
      ctx.shadowBlur = 10;
      ctx.beginPath();
      ctx.moveTo(pouchX + 10, scanLineY);
      ctx.lineTo(pouchX + pouchW - 10, scanLineY);
      ctx.stroke();
      ctx.shadowBlur = 0;

      animationFrameRef.current = requestAnimationFrame(renderSimulator);
    };

    renderSimulator();

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isSimulatorActive, simulatorSample, capturedImage, isOpen]);

  // Execute snapshot capture
  const performActualCapture = () => {
    playShutterSound();
    setIsShutterActive(true);
    setTimeout(() => setIsShutterActive(false), 220);

    if (isSimulatorActive && simulatorCanvasRef.current) {
      const canvas = simulatorCanvasRef.current;
      const dataUrl = canvas.toDataURL('image/jpeg', 0.95);
      setCapturedImage(dataUrl);
      return;
    }

    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;

    const width = video.videoWidth || 1280;
    const height = video.videoHeight || 720;
    canvas.width = width;
    canvas.height = height;

    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.drawImage(video, 0, 0, width, height);
      const dataUrl = canvas.toDataURL('image/jpeg', 0.95);
      setCapturedImage(dataUrl);
      stopCamera();
    }
  };

  // Trigger shoot with optional countdown
  const handleShootPhoto = () => {
    if (useTimer) {
      setCountdown(3);
      playBeepSound();

      let count = 3;
      countdownTimerRef.current = setInterval(() => {
        count -= 1;
        if (count > 0) {
          setCountdown(count);
          playBeepSound();
        } else {
          clearInterval(countdownTimerRef.current);
          countdownTimerRef.current = null;
          setCountdown(null);
          performActualCapture();
        }
      }, 1000);
    } else {
      performActualCapture();
    }
  };

  // Keyboard shortcut: Spacebar or Enter triggers photo shoot
  useEffect(() => {
    if (!isOpen || capturedImage) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.code === 'Space' && e.target === document.body) {
        e.preventDefault();
        handleShootPhoto();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, capturedImage, useTimer, isSimulatorActive]);

  const handleRetake = () => {
    setCapturedImage(null);
    if (isSimulatorActive) {
      // Simulator continues
    } else {
      startCamera(selectedDeviceId || undefined, facingMode);
    }
  };

  const handleConfirmPhoto = () => {
    if (capturedImage) {
      onCapture(capturedImage, selectedSurface);
      onClose();
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      const reader = new FileReader();
      reader.onload = (event) => {
        if (event.target?.result) {
          setCapturedImage(event.target.result as string);
          stopCamera();
        }
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSwitchLens = () => {
    const nextMode = facingMode === 'environment' ? 'user' : 'environment';
    setFacingMode(nextMode);
    startCamera(undefined, nextMode);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-slate-950/85 backdrop-blur-xs animate-in fade-in duration-150">
      <div className="w-full max-w-3xl bg-slate-900 border border-slate-700 rounded-xl shadow-2xl overflow-hidden flex flex-col text-slate-100 max-h-[95vh]">
        {/* Header Bar */}
        <div className="px-4 sm:px-6 py-3 bg-slate-850 border-b border-slate-700/80 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center shadow-inner">
              <Camera className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-sm font-bold text-white tracking-wide">
                  Optical Product Scanner & Live Camera
                </h3>
                <span className="text-[10px] bg-emerald-950 text-emerald-300 border border-emerald-700/50 px-1.5 py-0.2 rounded font-mono font-semibold">
                  LIVE READY
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                Legal Metrology Packaging Inspection • High-Definition Optical Frame Capture
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {/* Quick Camera Mode Switcher */}
            <div className="hidden sm:flex items-center space-x-1 bg-slate-800 p-1 rounded-lg border border-slate-700 text-xs">
              <button
                type="button"
                onClick={() => {
                  setIsSimulatorActive(false);
                  startCamera();
                }}
                className={`px-2.5 py-1 rounded text-xs font-medium transition cursor-pointer flex items-center space-x-1.5 ${
                  !isSimulatorActive
                    ? 'bg-[#0f2942] text-amber-300 font-bold border border-amber-400/40 shadow-xs'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
                title="Use physical webcam/camera connected to this machine"
              >
                <Camera className="w-3.5 h-3.5" />
                <span>Webcam</span>
              </button>
              <button
                type="button"
                onClick={() => {
                  stopCamera();
                  setIsSimulatorActive(true);
                }}
                className={`px-2.5 py-1 rounded text-xs font-medium transition cursor-pointer flex items-center space-x-1.5 ${
                  isSimulatorActive
                    ? 'bg-amber-500 text-slate-950 font-bold shadow-xs'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
                title="Use Live Optical Camera Feed with calibrated packaging"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>Optical Feed</span>
              </button>
            </div>

            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition cursor-pointer"
              title="Close Camera"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Viewport Area */}
        <div className="relative flex-1 bg-black overflow-hidden flex items-center justify-center min-h-[380px] max-h-[480px]">
          {/* Shutter White Flash Animation */}
          {isShutterActive && (
            <div className="absolute inset-0 z-40 bg-white transition-opacity duration-200 pointer-events-none" />
          )}

          {/* Countdown Overlay (3... 2... 1...) */}
          {countdown !== null && (
            <div className="absolute inset-0 z-35 flex items-center justify-center bg-black/50 backdrop-blur-xs">
              <div className="w-24 h-24 rounded-full bg-emerald-500/30 border-2 border-emerald-400 flex items-center justify-center animate-ping duration-1000">
                <span className="text-5xl font-black text-white font-mono">{countdown}</span>
              </div>
            </div>
          )}

          {/* Hidden Canvas for standard video extraction */}
          <canvas ref={canvasRef} className="hidden" />

          {/* Case 1: Photo has been shot - Review & Confirm Screen */}
          {capturedImage ? (
            <div className="relative w-full h-full flex flex-col items-center justify-center p-4 bg-slate-950">
              <img
                src={capturedImage}
                alt="Captured Commodity Label"
                className="max-h-[360px] w-auto object-contain rounded-lg border-2 border-emerald-500/50 shadow-2xl"
              />
              <div className="absolute top-4 left-4 bg-emerald-900/90 border border-emerald-500 text-emerald-200 px-3 py-1 rounded-md text-xs font-semibold flex items-center space-x-2 shadow-lg">
                <Check className="w-4 h-4 text-emerald-300" />
                <span>Photo Captured Successfully • Ready for OCR & Rule Engine</span>
              </div>
            </div>
          ) : isSimulatorActive ? (
            /* Case 2: Live Interactive Optical Simulator */
            <div className="relative w-full h-full flex items-center justify-center">
              <canvas
                ref={simulatorCanvasRef}
                className="w-full h-full object-contain max-h-[440px]"
              />
              <div className="absolute top-3 left-3 bg-amber-900/80 border border-amber-600 text-amber-200 px-2.5 py-0.5 rounded text-[11px] font-mono flex items-center space-x-1.5 shadow z-10">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Live Optical Packaging Feed</span>
              </div>
              {cameraNotice && (
                <div className="absolute top-10 left-3 right-3 z-10 bg-slate-900/90 border border-amber-500/60 text-amber-200 px-3 py-1.5 rounded text-xs font-sans shadow-lg flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
                    <span className="text-[11px]">{cameraNotice}</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => {
                      setIsSimulatorActive(false);
                      startCamera();
                    }}
                    className="ml-2 px-2 py-0.5 bg-amber-500 text-slate-950 font-bold rounded text-[10px] hover:bg-amber-400 shrink-0 cursor-pointer"
                  >
                    Try Webcam
                  </button>
                </div>
              )}
            </div>
          ) : !cameraError ? (
            /* Case 3: Real Hardware Camera Feed */
            <div className="relative w-full h-full flex items-center justify-center">
              {isLoadingCamera && (
                <div className="absolute inset-0 z-20 flex flex-col items-center justify-center bg-slate-950 space-y-3">
                  <div className="w-10 h-10 border-4 border-emerald-500/30 border-t-emerald-400 rounded-full animate-spin" />
                  <p className="text-xs text-slate-300 font-medium">
                    Initializing Optical Sensor & Camera Stream...
                  </p>
                </div>
              )}

              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                onLoadedMetadata={() => {
                  if (videoRef.current) {
                    videoRef.current.play().catch(() => {});
                  }
                }}
                className="w-full h-full object-contain max-h-[440px]"
              />

              {/* Viewfinder Target Reticle Overlay */}
              <div className="absolute inset-6 sm:inset-10 border-2 border-dashed border-emerald-400/80 rounded-lg pointer-events-none flex flex-col justify-between p-3.5">
                <div className="flex justify-between items-start">
                  <div className="flex items-center space-x-1.5 bg-black/60 backdrop-blur-xs text-emerald-300 px-2 py-0.5 rounded text-[10px] font-mono uppercase font-bold border border-emerald-500/30">
                    <ScanLine className="w-3.5 h-3.5 animate-pulse text-emerald-400" />
                    <span>Align Principal Display Panel (PDP)</span>
                  </div>
                  <div className="bg-black/60 backdrop-blur-xs text-slate-300 px-2 py-0.5 rounded text-[10px] font-mono border border-slate-700">
                    {facingMode === 'user' ? 'Front / Webcam' : 'Rear Lens'}
                  </div>
                </div>

                <div className="text-center text-[11px] font-medium text-slate-100 bg-black/70 backdrop-blur-xs px-3.5 py-1 rounded-full mx-auto shadow-md border border-slate-700/60">
                  Keep statutory label flat, well-lit, and inside the guidelines
                </div>

                <div className="flex justify-between items-end text-[10px] font-mono text-emerald-400/90">
                  <span>[ OPTICAL 300 DPI ]</span>
                  <span>[ PRESS SPACEBAR OR CLICK SHOOT ]</span>
                </div>
              </div>
            </div>
          ) : (
            /* Case 4: Camera Notice / Permission / Device Error Screen */
            <div className="p-6 text-center space-y-4 max-w-md">
              <div className="w-12 h-12 rounded-full bg-amber-500/20 border border-amber-500/40 text-amber-400 flex items-center justify-center mx-auto">
                <AlertCircle className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-white">Live Camera Notice</h4>
                <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                  {cameraError}
                </p>
              </div>

              <div className="pt-2 flex flex-col sm:flex-row gap-2 justify-center">
                <Button
                  variant="primary"
                  size="sm"
                  leftIcon={<RefreshCw className="w-3.5 h-3.5" />}
                  onClick={() => startCamera()}
                >
                  Retry Camera
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  leftIcon={<Sparkles className="w-3.5 h-3.5" />}
                  onClick={() => setIsSimulatorActive(true)}
                >
                  Use Optical Simulator
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="text-slate-200 border-slate-700"
                  leftIcon={<Upload className="w-3.5 h-3.5" />}
                  onClick={() => fileInputRef.current?.click()}
                >
                  Upload File
                </Button>
              </div>
            </div>
          )}
        </div>

        {/* Surface Selection & Quick Bar */}
        <div className="px-4 py-2.5 bg-slate-850 border-t border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 text-xs">
          <div className="flex items-center space-x-2 text-slate-300">
            <span className="font-semibold text-slate-200">Packaging Surface:</span>
            <div className="flex items-center space-x-1.5 overflow-x-auto">
              {(['Front (PDP)', 'Back Panel', 'Side Panel', 'Top/Bottom'] as SurfaceType[]).map((surface) => (
                <button
                  key={surface}
                  type="button"
                  onClick={() => setSelectedSurface(surface)}
                  className={`px-2.5 py-1 rounded text-xs transition cursor-pointer ${
                    selectedSurface === surface
                      ? 'bg-emerald-600 text-white font-bold shadow-xs'
                      : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                  }`}
                >
                  {surface}
                </button>
              ))}
            </div>
          </div>

          {/* Quick Hardware Controls */}
          {!capturedImage && !cameraError && (
            <div className="flex items-center space-x-2">
              {/* Device Selector (if multiple webcams available) */}
              {videoDevices.length > 1 && (
                <select
                  value={selectedDeviceId}
                  onChange={(e) => {
                    setSelectedDeviceId(e.target.value);
                    startCamera(e.target.value);
                  }}
                  className="bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded px-2 py-1"
                >
                  {videoDevices.map((dev, i) => (
                    <option key={dev.deviceId} value={dev.deviceId}>
                      {dev.label || `Camera ${i + 1}`}
                    </option>
                  ))}
                </select>
              )}

              {/* 3s Countdown Timer Toggle */}
              <button
                type="button"
                onClick={() => setUseTimer(!useTimer)}
                className={`flex items-center space-x-1 px-2.5 py-1 rounded text-xs border transition cursor-pointer ${
                  useTimer
                    ? 'bg-amber-500/20 text-amber-300 border-amber-500/40 font-bold'
                    : 'bg-slate-800 text-slate-400 border-slate-700 hover:text-white'
                }`}
                title="Toggle 3-Second Countdown Timer"
              >
                <Timer className="w-3.5 h-3.5" />
                <span>{useTimer ? '3s Timer: ON' : '3s Timer'}</span>
              </button>

              {/* Switch Front/Back Lens */}
              <button
                type="button"
                onClick={handleSwitchLens}
                className="p-1.5 rounded text-slate-400 hover:text-white hover:bg-slate-800 border border-slate-700 transition cursor-pointer"
                title="Switch Camera Lens (Front/Back)"
              >
                <RotateCw className="w-3.5 h-3.5" />
              </button>
            </div>
          )}

          {/* Simulator sample switcher */}
          {isSimulatorActive && !capturedImage && (
            <div className="flex items-center space-x-2">
              <span className="text-slate-400">Sample:</span>
              <button
                type="button"
                onClick={() => setSimulatorSample('lakme')}
                className={`px-2.5 py-1 rounded text-xs transition font-semibold cursor-pointer ${
                  simulatorSample === 'lakme' ? 'bg-amber-500 text-slate-950 font-bold shadow-xs' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                }`}
              >
                ✨ Lakmé Sunscreen (56g)
              </button>
              <button
                type="button"
                onClick={() => setSimulatorSample('mustard')}
                className={`px-2 py-0.5 rounded text-xs ${
                  simulatorSample === 'mustard' ? 'bg-amber-600 text-white font-bold' : 'bg-slate-800 text-slate-300'
                }`}
              >
                Mustard Oil
              </button>
              <button
                type="button"
                onClick={() => setSimulatorSample('facewash')}
                className={`px-2 py-0.5 rounded text-xs ${
                  simulatorSample === 'facewash' ? 'bg-emerald-600 text-white font-bold' : 'bg-slate-800 text-slate-300'
                }`}
              >
                Neem Face Wash
              </button>
            </div>
          )}
        </div>

        {/* Action Controls Footer */}
        <div className="p-4 bg-slate-900 border-t border-slate-800 flex items-center justify-between">
          {/* Left Action: Upload File Alternative */}
          <div className="flex items-center space-x-2">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileUpload}
              className="hidden"
            />
            <Button
              variant="outline"
              size="sm"
              className="text-slate-300 border-slate-700 hover:bg-slate-800"
              leftIcon={<Upload className="w-3.5 h-3.5" />}
              onClick={() => fileInputRef.current?.click()}
            >
              Upload Photo Instead
            </Button>

            {!isSimulatorActive && !capturedImage && (
              <button
                type="button"
                onClick={() => setIsSimulatorActive(true)}
                className="text-xs text-slate-400 hover:text-slate-200 underline hidden sm:inline"
              >
                Test with Optical Simulator
              </button>
            )}

            {isSimulatorActive && !capturedImage && (
              <button
                type="button"
                onClick={() => {
                  setIsSimulatorActive(false);
                  startCamera();
                }}
                className="text-xs text-emerald-400 hover:text-emerald-300 underline"
              >
                Back to Real Webcam
              </button>
            )}
          </div>

          {/* Right Action: Shoot Photo or Review Confirm */}
          <div className="flex items-center space-x-2.5">
            {capturedImage ? (
              <>
                <Button
                  variant="outline"
                  size="md"
                  className="text-slate-200 border-slate-700 hover:bg-slate-800 font-semibold"
                  leftIcon={<RefreshCw className="w-4 h-4" />}
                  onClick={handleRetake}
                >
                  Retake Photo
                </Button>
                <Button
                  variant="success"
                  size="md"
                  className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold px-5 shadow-lg border-emerald-500"
                  leftIcon={<Check className="w-4 h-4" />}
                  onClick={handleConfirmPhoto}
                >
                  Use This Photo for Inspection
                </Button>
              </>
            ) : (
              <button
                type="button"
                onClick={handleShootPhoto}
                disabled={isLoadingCamera}
                className={`flex items-center space-x-2.5 px-6 py-2.5 rounded-lg font-bold text-sm text-white shadow-xl transition-all transform active:scale-95 cursor-pointer border ${
                  isLoadingCamera
                    ? 'bg-slate-700 border-slate-600 opacity-50 cursor-not-allowed'
                    : 'bg-emerald-600 hover:bg-emerald-500 border-emerald-400/50 hover:shadow-emerald-500/25 ring-2 ring-emerald-500/30'
                }`}
              >
                <Camera className="w-5 h-5 text-white animate-pulse" />
                <span>
                  {countdown !== null ? `Shooting in ${countdown}s...` : 'Shoot Photo Now'}
                </span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
