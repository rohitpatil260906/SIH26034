import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Button } from '../ui/Button';
import {
  Camera,
  RotateCw,
  X,
  Check,
  RefreshCw,
  Upload,
  Timer,
  ScanLine,
  Lock,
  CameraOff
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
  const [facingMode, setFacingMode] = useState<'environment' | 'user'>('user'); // Default to 'user' for laptop webcam compatibility
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [errorTitle, setErrorTitle] = useState<string | null>(null);
  const [exactErrorDetails, setExactErrorDetails] = useState<string | null>(null);
  const [permissionQueryState, setPermissionQueryState] = useState<string | null>(null);
  const [errorType, setErrorType] = useState<'permission' | 'not_found' | 'in_use' | 'security' | 'constraints' | 'unsupported' | 'policy' | 'unknown' | null>(null);
  const [isPermissionDenied, setIsPermissionDenied] = useState<boolean>(false);
  const [isLoadingCamera, setIsLoadingCamera] = useState<boolean>(false);
  const [selectedSurface, setSelectedSurface] = useState<SurfaceType>(surface || defaultSurface);
  const [isShutterActive, setIsShutterActive] = useState<boolean>(false);

  // Available camera devices (USB cams, integrated cams, etc.)
  const [videoDevices, setVideoDevices] = useState<MediaDeviceInfo[]>([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState<string>('');

  // 3-second countdown timer for positioning physical items
  const [useTimer, setUseTimer] = useState<boolean>(false);
  const [countdown, setCountdown] = useState<number | null>(null);

  // Persistent reference to stream for leak-free track cleanup across renders and closures
  const streamRef = useRef<MediaStream | null>(null);
  const activeRequestIdRef = useRef<number>(0);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const countdownTimerRef = useRef<any>(null);

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
      if (videoInputs.length > 0 && !selectedDeviceId && videoInputs[0].deviceId) {
        setSelectedDeviceId(videoInputs[0].deviceId);
      }
    } catch (e) {
      console.warn('[CameraCaptureModal] Could not enumerate video devices:', e);
    }
  }, [selectedDeviceId]);

  // Callback ref to attach stream to video element whenever it mounts
  const attachVideoRef = useCallback((node: HTMLVideoElement | null) => {
    videoRef.current = node;
    if (node && streamRef.current) {
      if (node.srcObject !== streamRef.current) {
        node.srcObject = streamRef.current;
      }
      node.muted = true;
      node.playsInline = true;
      node.setAttribute('playsinline', 'true');
      node.setAttribute('autoplay', 'true');
      node.setAttribute('muted', 'true');
      const playPromise = node.play();
      if (playPromise !== undefined) {
        playPromise.catch(e => console.warn('[CameraCaptureModal] Callback ref play warning:', e));
      }
    }
  }, []);

  // Guaranteed clean camera track shutdown
  const stopCamera = useCallback(() => {
    activeRequestIdRef.current++;
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => {
        try {
          track.stop();
        } catch (e) {
          console.warn('[CameraCaptureModal] Error stopping streamRef track:', e);
        }
      });
      streamRef.current = null;
    }
    setStream(null);
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    if (countdownTimerRef.current) {
      clearInterval(countdownTimerRef.current);
      countdownTimerRef.current = null;
    }
    setCountdown(null);
  }, []);

  // Start device camera via navigator.mediaDevices.getUserMedia({ video: true, audio: false })
  const startCamera = useCallback(async (deviceId?: string) => {
    const currentRequestId = ++activeRequestIdRef.current;
    setIsLoadingCamera(true);
    setCameraError(null);
    setErrorTitle(null);
    setExactErrorDetails(null);
    setErrorType(null);
    setIsPermissionDenied(false);

    // Query browser Permissions API if available to inspect and track state
    if (typeof navigator !== 'undefined' && navigator.permissions && navigator.permissions.query) {
      try {
        const pStatus = await navigator.permissions.query({ name: 'camera' as any });
        setPermissionQueryState(pStatus.state);
        pStatus.onchange = () => {
          setPermissionQueryState(pStatus.state);
          if (pStatus.state === 'granted' && !streamRef.current) {
            startCamera(deviceId);
          }
        };
      } catch {
        // Permissions query not supported for camera in some browsers
      }
    }

    // Check secure context
    const isSecure = typeof window !== 'undefined' && (
      window.isSecureContext ||
      window.location.protocol === 'https:' ||
      window.location.hostname === 'localhost' ||
      window.location.hostname === '127.0.0.1'
    );

    if (!isSecure) {
      setIsLoadingCamera(false);
      setErrorType('security');
      setErrorTitle('Secure HTTPS Connection Required');
      setCameraError('Camera access is restricted to secure origins (HTTPS). Please ensure you are accessing the deployed application over https://.');
      setExactErrorDetails(`Current origin is not secure: ${window.location.protocol}//${window.location.host}`);
      return;
    }

    // Resolve mediaDevices API with fallback for older browsers
    const mediaDevices = navigator?.mediaDevices || (
      (navigator as any)?.getUserMedia ? {
        getUserMedia: (c: MediaStreamConstraints) =>
          new Promise<MediaStream>((resolve, reject) => {
            (navigator as any).getUserMedia(c, resolve, reject);
          }),
        enumerateDevices: () => Promise.resolve([])
      } : null
    );

    if (!mediaDevices || typeof mediaDevices.getUserMedia !== 'function') {
      setIsLoadingCamera(false);
      setErrorType('unsupported');
      setErrorTitle('Camera API Not Supported');
      setCameraError('The Camera API (navigator.mediaDevices.getUserMedia) is not supported by your current browser or Webview.');
      setExactErrorDetails(`navigator.mediaDevices: ${typeof navigator?.mediaDevices}, isSecureContext: ${window.isSecureContext}`);
      return;
    }

    try {
      let acquiredStream: MediaStream | null = null;

      // 1. Try with exact deviceId if selected by user
      if (deviceId && deviceId.trim()) {
        try {
          acquiredStream = await mediaDevices.getUserMedia({
            video: { deviceId: { exact: deviceId } },
            audio: false
          });
        } catch (deviceErr) {
          console.warn('[CameraCaptureModal] Selected deviceId failed, falling back to basic video constraint:', deviceErr);
          acquiredStream = await mediaDevices.getUserMedia({
            video: true,
            audio: false
          });
        }
      } else {
        // 2. Standard native browser camera request
        acquiredStream = await mediaDevices.getUserMedia({
          video: true,
          audio: false
        });
      }

      // Check if this request was superseded while waiting for user interaction
      if (activeRequestIdRef.current !== currentRequestId) {
        acquiredStream.getTracks().forEach(t => {
          try { t.stop(); } catch {}
        });
        return;
      }

      // Stop previous stream tracks cleanly now that new stream is ready
      if (streamRef.current && streamRef.current !== acquiredStream) {
        streamRef.current.getTracks().forEach(t => {
          try { t.stop(); } catch {}
        });
      }

      streamRef.current = acquiredStream;
      setStream(acquiredStream);
      setIsLoadingCamera(false);
      setCameraError(null);
      setErrorTitle(null);
      setExactErrorDetails(null);
      setErrorType(null);
      setIsPermissionDenied(false);

      if (videoRef.current) {
        videoRef.current.srcObject = acquiredStream;
        videoRef.current.muted = true;
        videoRef.current.playsInline = true;
        videoRef.current.setAttribute('playsinline', 'true');
        videoRef.current.setAttribute('autoplay', 'true');
        videoRef.current.setAttribute('muted', 'true');
        const playPromise = videoRef.current.play();
        if (playPromise !== undefined) {
          playPromise.catch(playErr => {
            console.warn('[CameraCaptureModal] Video play promise caught:', playErr);
          });
        }
      }

      refreshDevices();
    } catch (err: any) {
      if (activeRequestIdRef.current !== currentRequestId) return;
      setIsLoadingCamera(false);

      const errName: string = err?.name || '';
      const errMsg: string = err?.message || '';
      console.error('[CameraCaptureModal] getUserMedia failed:', errName, errMsg, err);

      const isPolicyBlocked =
        errMsg.toLowerCase().includes('permissions policy') ||
        errMsg.toLowerCase().includes('feature policy') ||
        errMsg.toLowerCase().includes('disallowed');

      const isSystemBlocked =
        errMsg.toLowerCase().includes('system') ||
        errMsg.toLowerCase().includes('operating system');

      const technicalSummary = `Error: [${errName || 'Error'}] ${errMsg || 'No error message provided'} | Origin: ${window.location.origin} | Protocol: ${window.location.protocol}`;
      setExactErrorDetails(technicalSummary);

      if (errName === 'NotAllowedError' || errName === 'PermissionDeniedError') {
        setIsPermissionDenied(true);
        if (isPolicyBlocked) {
          setErrorType('policy');
          setErrorTitle('Camera Blocked by Permissions Policy');
          setCameraError(
            'Camera access is disallowed by permissions policy. If this application is running inside an iframe or preview bar on Vercel, open the direct URL in a new browser tab.'
          );
        } else if (isSystemBlocked) {
          setErrorType('permission');
          setErrorTitle('Camera Blocked by Operating System');
          setCameraError(
            'Your operating system (Windows/macOS) is blocking camera access for your browser. Please check OS Privacy & Security > Camera permissions.'
          );
        } else {
          setErrorType('permission');
          setErrorTitle('Camera Permission Denied');
          setCameraError(
            'Camera permission was denied in your browser for this URL. Please click the camera/lock icon in your browser address bar, choose "Always allow", and click "Retry Camera".'
          );
        }
      } else if (errName === 'NotFoundError' || errName === 'DevicesNotFoundError') {
        setIsPermissionDenied(false);
        setErrorType('not_found');
        setErrorTitle('No Camera Detected');
        setCameraError(
          'No camera device was detected on your system. Please connect a webcam or enable your device camera and click "Retry Camera".'
        );
      } else if (errName === 'NotReadableError' || errName === 'TrackStartError') {
        setIsPermissionDenied(false);
        setErrorType('in_use');
        setErrorTitle('Camera Already In Use');
        setCameraError(
          'The camera is currently locked or in use by another application (Zoom, Teams, Meet, etc.) or another browser tab. Close other apps using the camera and click "Retry Camera".'
        );
      } else if (errName === 'OverconstrainedError') {
        setIsPermissionDenied(false);
        setErrorType('constraints');
        setErrorTitle('Camera Constraints Error');
        setCameraError(
          `The requested camera constraints are not supported by your hardware (${(err as any)?.constraint || 'unsupported'}). Click "Retry Camera" to reset.`
        );
      } else if (errName === 'SecurityError') {
        setIsPermissionDenied(false);
        setErrorType('security');
        setErrorTitle('Browser Security Restriction');
        setCameraError(
          'Camera access was restricted by browser security policies. Ensure the application is accessed over HTTPS directly.'
        );
      } else if (errName === 'TypeError') {
        setIsPermissionDenied(false);
        setErrorType('constraints');
        setErrorTitle('Camera Configuration Error');
        setCameraError(
          'Invalid camera constraints were requested. Click "Retry Camera" to reset to standard constraints.'
        );
      } else if (errName === 'AbortError') {
        setIsPermissionDenied(false);
        setErrorType('unknown');
        setErrorTitle('Camera Operation Aborted');
        setCameraError(
          'The camera operation was interrupted or aborted by the browser. Click "Retry Camera" to try again.'
        );
      } else {
        setIsPermissionDenied(false);
        setErrorType('unknown');
        setErrorTitle('Camera Unavailable');
        setCameraError(
          errMsg || 'An unexpected error occurred while requesting device camera access. Check browser console for details.'
        );
      }
    }
  }, [refreshDevices]);

  // Synchronize stream with video element
  useEffect(() => {
    if (videoRef.current && stream && !capturedImage) {
      if (videoRef.current.srcObject !== stream) {
        videoRef.current.srcObject = stream;
      }
      videoRef.current.muted = true;
      videoRef.current.playsInline = true;
      const playPromise = videoRef.current.play();
      if (playPromise !== undefined) {
        playPromise.catch(err => {
          console.warn('[CameraCaptureModal] Video autoplay aborted:', err);
        });
      }
    }
  }, [stream, capturedImage]);

  // Handle open / close lifecycle
  useEffect(() => {
    if (!isOpen) {
      stopCamera();
      setCapturedImage(null);
      setCameraError(null);
      setErrorTitle(null);
      setExactErrorDetails(null);
      setErrorType(null);
      setIsPermissionDenied(false);
      return;
    }

    setSelectedSurface(surface || defaultSurface);
    startCamera(selectedDeviceId || undefined);

    return () => {
      stopCamera();
    };
  }, [isOpen]);

  // Execute snapshot capture directly from webcam stream
  const performActualCapture = () => {
    playShutterSound();
    setIsShutterActive(true);
    setTimeout(() => setIsShutterActive(false), 220);

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

  // Keyboard shortcut: Spacebar triggers photo shoot
  useEffect(() => {
    if (!isOpen || capturedImage || cameraError || isLoadingCamera) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.code === 'Space' && e.target === document.body) {
        e.preventDefault();
        handleShootPhoto();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, capturedImage, cameraError, isLoadingCamera, useTimer]);

  const handleRetake = () => {
    setCapturedImage(null);
    startCamera(selectedDeviceId || undefined);
  };

  const handleConfirmPhoto = () => {
    if (capturedImage) {
      stopCamera();
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

  const handleSwitchLens = async () => {
    const nextMode = facingMode === 'environment' ? 'user' : 'environment';
    setFacingMode(nextMode);
    try {
      if (navigator?.mediaDevices?.getUserMedia) {
        const switchedStream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: nextMode },
          audio: false
        });
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(t => t.stop());
        }
        streamRef.current = switchedStream;
        setStream(switchedStream);
        if (videoRef.current) {
          videoRef.current.srcObject = switchedStream;
          videoRef.current.muted = true;
          videoRef.current.playsInline = true;
          videoRef.current.play().catch(() => {});
        }
      }
    } catch {
      startCamera();
    }
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
                  Live Camera Scanner
                </h3>
                {stream && !cameraError && (
                  <span className="text-[10px] bg-emerald-950 text-emerald-300 border border-emerald-700/50 px-1.5 py-0.2 rounded font-mono font-semibold">
                    LIVE
                  </span>
                )}
              </div>
              <p className="text-[11px] text-slate-400">
                Legal Metrology Packaging Inspection • Live Webcam Feed
              </p>
            </div>
          </div>

          <button
            onClick={() => {
              stopCamera();
              onClose();
            }}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition cursor-pointer"
            title="Close Camera"
          >
            <X className="w-5 h-5" />
          </button>
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
                alt="Captured Package Label"
                className="max-h-[360px] w-auto object-contain rounded-lg border-2 border-emerald-500/50 shadow-2xl"
              />
              <div className="absolute top-4 left-4 bg-emerald-900/90 border border-emerald-500 text-emerald-200 px-3 py-1 rounded-md text-xs font-semibold flex items-center space-x-2 shadow-lg">
                <Check className="w-4 h-4 text-emerald-300" />
                <span>Photo Captured Successfully • Ready for Inspection</span>
              </div>
            </div>
          ) : cameraError ? (
            /* Case 2: Camera Permission / Device Error Screen */
            <div className="p-6 sm:p-8 text-center space-y-4 max-w-lg mx-auto w-full">
              <div
                className={`w-14 h-14 rounded-full flex items-center justify-center mx-auto ${
                  errorType === 'permission' || errorType === 'policy'
                    ? 'bg-amber-500/20 border border-amber-500/40 text-amber-400'
                    : 'bg-rose-500/20 border border-rose-500/40 text-rose-400'
                }`}
              >
                {errorType === 'permission' || errorType === 'policy' ? (
                  <Lock className="w-7 h-7" />
                ) : (
                  <CameraOff className="w-7 h-7" />
                )}
              </div>
              <div>
                <h4 className="text-base font-bold text-white">
                  {errorTitle || 'Camera Unavailable'}
                </h4>
                <p className="text-xs text-slate-300 mt-2 leading-relaxed">
                  {cameraError}
                </p>

                {/* Specific Actionable Guidance */}
                {(errorType === 'permission' || errorType === 'policy') && (
                  <p className="text-[11px] text-amber-300/90 mt-2.5 bg-amber-950/40 border border-amber-800/40 rounded p-2.5 leading-normal text-left">
                    {errorType === 'policy'
                      ? '⚠️ Permissions Policy Notice: If testing inside a Vercel preview toolbar or iframe, camera access may be restricted by the embedding parent frame. Please open the deployed Vercel URL directly in a full browser tab.'
                      : '💡 To grant permission: Click the camera or lock/tune icon in your browser address bar (top-left or top-right of URL), select "Allow" for Camera, and click "Retry Camera" below.'}
                  </p>
                )}

                {/* Visible Exact Browser Diagnostic Box */}
                {exactErrorDetails && (
                  <div className="mt-3 p-3 bg-slate-950/90 border border-slate-800 rounded text-left font-mono">
                    <div className="flex items-center justify-between text-[10px] font-bold text-slate-400 border-b border-slate-800/80 pb-1 mb-1.5">
                      <span>EXACT BROWSER DIAGNOSTIC</span>
                      <span className={`text-[10px] uppercase font-bold px-1 rounded ${
                        errorType === 'permission' || errorType === 'policy'
                          ? 'bg-amber-950 text-amber-300 border border-amber-800/60'
                          : 'bg-rose-950 text-rose-300 border border-rose-800/60'
                      }`}>
                        {errorType || 'ERROR'}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-300 break-all leading-relaxed">
                      {exactErrorDetails}
                    </p>
                    {permissionQueryState && (
                      <p className="text-[10px] text-slate-400 mt-1">
                        Permissions API State: <span className="text-amber-400 font-bold">{permissionQueryState}</span>
                      </p>
                    )}
                  </div>
                )}
              </div>

              <div className="pt-2 flex flex-col sm:flex-row gap-2.5 justify-center">
                <Button
                  variant="primary"
                  size="md"
                  leftIcon={<RefreshCw className="w-4 h-4" />}
                  onClick={() => startCamera(selectedDeviceId || undefined)}
                >
                  Retry Camera
                </Button>
                <Button
                  variant="outline"
                  size="md"
                  className="text-slate-200 border-slate-700 hover:bg-slate-800"
                  leftIcon={<Upload className="w-4 h-4" />}
                  onClick={() => fileInputRef.current?.click()}
                >
                  Upload Photo Instead
                </Button>
              </div>
            </div>
          ) : (
            /* Case 3: Real Hardware Camera Live Feed */
            <div className="relative w-full h-full flex items-center justify-center">
              {isLoadingCamera && (
                <div className="absolute inset-0 z-20 flex flex-col items-center justify-center bg-slate-950 space-y-3">
                  <div className="w-10 h-10 border-4 border-emerald-500/30 border-t-emerald-400 rounded-full animate-spin" />
                  <p className="text-xs text-slate-300 font-medium">
                    Connecting to Camera & Opening Live Stream...
                  </p>
                </div>
              )}

              <video
                ref={attachVideoRef}
                autoPlay
                playsInline
                muted
                onLoadedMetadata={() => {
                  if (videoRef.current) {
                    videoRef.current.play().catch(err => console.warn('Video autoplay aborted:', err));
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
                  <span>[ LIVE OPTICAL FEED ]</span>
                  <span>[ PRESS SPACEBAR OR CLICK SHOOT ]</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Surface Selection & Hardware Bar */}
        <div className="px-4 py-2.5 bg-slate-850 border-t border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 text-xs">
          <div className="flex items-center space-x-2 text-slate-300">
            <span className="font-semibold text-slate-200">Packaging Surface:</span>
            <div className="flex items-center space-x-1.5 overflow-x-auto">
              {(['Front (PDP)', 'Back Panel', 'Side Panel', 'Top/Bottom'] as SurfaceType[]).map((surf) => (
                <button
                  key={surf}
                  type="button"
                  onClick={() => setSelectedSurface(surf)}
                  className={`px-2.5 py-1 rounded text-xs transition cursor-pointer ${
                    selectedSurface === surf
                      ? 'bg-emerald-600 text-white font-bold shadow-xs'
                      : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                  }`}
                >
                  {surf}
                </button>
              ))}
            </div>
          </div>

          {/* Hardware Controls */}
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
            ) : !cameraError ? (
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
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
};
