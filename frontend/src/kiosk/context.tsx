import React, { createContext, useCallback, useContext, useMemo, useState } from "react";

export const SCREENS = [
  "welcome",
  "language",
  "identify",
  "consent",
  "accessibility",
  "complaint",
  "socrates",
  "ayush",
  "emergency",
  "scan",
  "review",
  "summary",
  "token",
  "reset",
  "dashboard",
  "doctor",
] as const;

export type ScreenId = (typeof SCREENS)[number];

export const SCREEN_TITLES: Record<ScreenId, string> = {
  welcome: "Welcome",
  language: "Language",
  identify: "Identify",
  consent: "Consent",
  accessibility: "Accessibility",
  complaint: "Complaint",
  socrates: "Follow-up",
  ayush: "AYUSH History",
  emergency: "Emergency",
  scan: "Scan Docs",
  review: "Review OCR",
  summary: "Summary",
  token: "Token",
  reset: "Session Reset",
  dashboard: "Patient App",
  doctor: "Doctor Portal",
};

export const INTERVIEW_STEPS: ScreenId[] = [
  "identify",
  "consent",
  "complaint",
  "socrates",
  "ayush",
  "scan",
  "review",
  "summary",
];

export type Lang = {
  code: string;
  label: string;
  native: string;
  greeting: string;
  speech: string;
  touchToStart: string;
};

export const LANGUAGES: Lang[] = [
  {
    code: "hi",
    label: "Hindi",
    native: "हिन्दी",
    greeting: "नमस्ते",
    speech: "hi-IN",
    touchToStart: "शुरू करने के लिए छुएं",
  },
  {
    code: "en",
    label: "English",
    native: "English",
    greeting: "Welcome",
    speech: "en-IN",
    touchToStart: "Touch to Start",
  },
  {
    code: "mr",
    label: "Marathi",
    native: "मराठी",
    greeting: "नमस्कार",
    speech: "mr-IN",
    touchToStart: "सुरू करण्यासाठी स्पर्श करा",
  },
  {
    code: "ta",
    label: "Tamil",
    native: "தமிழ்",
    greeting: "வணக்கம்",
    speech: "ta-IN",
    touchToStart: "தொடங்க தொடவும்",
  },
  {
    code: "bn",
    label: "Bengali",
    native: "বাংলা",
    greeting: "নমস্কার",
    speech: "bn-IN",
    touchToStart: "শুরু করতে স্পর্শ করুন",
  },
  {
    code: "te",
    label: "Telugu",
    native: "తెలుగు",
    greeting: "నమస్కారం",
    speech: "te-IN",
    touchToStart: "ప్రారంభించడానికి తాకండి",
  },
  {
    code: "gu",
    label: "Gujarati",
    native: "ગુજરાતી",
    greeting: "નમસ્તે",
    speech: "gu-IN",
    touchToStart: "શરૂ કરવા સ્પર્શ કરો",
  },
];

export type Patient = {
  name: string;
  age: string;
  gender: string;
  mobile: string;
  abha: string;
};

type KioskState = {
  screen: ScreenId;
  go: (s: ScreenId) => void;
  next: () => void;
  back: () => void;
  restart: () => void;
  lang: Lang;
  setLang: (l: Lang) => void;
  kioskFrame: boolean;
  setKioskFrame: (v: boolean) => void;
  ayushMode: boolean;
  setAyushMode: (v: boolean) => void;
  highContrast: boolean;
  setHighContrast: (v: boolean) => void;
  largeText: boolean;
  setLargeText: (v: boolean) => void;
  autoRead: boolean;
  setAutoRead: (v: boolean) => void;
  signAvatar: boolean;
  setSignAvatar: (v: boolean) => void;
  patient: Patient;
  setPatient: (p: Partial<Patient>) => void;
  complaint: string;
  setComplaint: (c: string) => void;
  severity: number;
  setSeverity: (n: number) => void;
  answers: Record<string, string>;
  setAnswer: (k: string, v: string) => void;
  speak: (text: string) => void;
  stopSpeech: () => void;
  speaking: boolean;
  sessionId: string | null;
  setSessionId: (id: string | null) => void;
  tokenNumber: string;
  setTokenNumber: (t: string) => void;
  ocrResult: any;
  setOcrResult: (r: any) => void;
  aiSummary: any;
  setAiSummary: (s: any) => void;
  x402Tx: any;
  setX402Tx: (tx: any) => void;
};

const Ctx = createContext<KioskState | null>(null);

export function useKiosk() {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useKiosk must be used inside KioskProvider");
  return ctx;
}

export function KioskProvider({ children }: { children: React.ReactNode }) {
  const [screen, setScreen] = useState<ScreenId>("welcome");
  const [lang, setLang] = useState<Lang>(LANGUAGES[1]!);
  const [kioskFrame, setKioskFrame] = useState(true);
  const [ayushMode, setAyushMode] = useState(true);
  const [highContrast, setHighContrast] = useState(false);
  const [largeText, setLargeText] = useState(false);
  const [autoRead, setAutoRead] = useState(false);
  const [signAvatar, setSignAvatar] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [complaint, setComplaint] = useState("");
  const [severity, setSeverity] = useState(5);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [tokenNumber, setTokenNumber] = useState("OPD-AYUSH-104");
  const [ocrResult, setOcrResult] = useState<any>(null);
  const [aiSummary, setAiSummary] = useState<any>(null);
  const [x402Tx, setX402Tx] = useState<any>(null);
  const [patient, setPatientState] = useState<Patient>({
    name: "Anita Sharma",
    age: "42",
    gender: "Female",
    mobile: "98765 43210",
    abha: "12-3456-7890-1234",
  });

  const stopSpeech = useCallback(() => {
    if (typeof window === "undefined" || !window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    setSpeaking(false);
  }, []);

  const speak = useCallback(
    (text: string) => {
      if (typeof window === "undefined" || !window.speechSynthesis) return;
      window.speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(text);
      u.lang = lang.speech;
      u.rate = 0.95;
      u.onend = () => setSpeaking(false);
      setSpeaking(true);
      window.speechSynthesis.speak(u);
    },
    [lang],
  );

  const go = useCallback(
    (s: ScreenId) => {
      stopSpeech();
      setScreen(s);
    },
    [stopSpeech],
  );

  const flow = useMemo(
    () => SCREENS.filter((s) => s !== "emergency" && s !== "dashboard" && (ayushMode || s !== "ayush")),
    [ayushMode],
  );

  const next = useCallback(() => {
    const i = flow.indexOf(screen);
    go(flow[Math.min(i + 1, flow.length - 1)] ?? "welcome");
  }, [flow, screen, go]);

  const back = useCallback(() => {
    const i = flow.indexOf(screen);
    go((i > 0 ? flow[i - 1] : "welcome") as ScreenId);
  }, [flow, screen, go]);

  const restart = useCallback(() => {
    setComplaint("");
    setAnswers({});
    setSeverity(5);
    setSessionId(null);
    setOcrResult(null);
    setAiSummary(null);
    setX402Tx(null);
    go("welcome");
  }, [go]);

  const value: KioskState = {
    screen,
    go,
    next,
    back,
    restart,
    lang,
    setLang,
    kioskFrame,
    setKioskFrame,
    ayushMode,
    setAyushMode,
    highContrast,
    setHighContrast,
    largeText,
    setLargeText,
    autoRead,
    setAutoRead,
    signAvatar,
    setSignAvatar,
    patient,
    setPatient: (p) => setPatientState((prev) => ({ ...prev, ...p })),
    complaint,
    setComplaint,
    severity,
    setSeverity,
    answers,
    setAnswer: (k, v) => setAnswers((prev) => ({ ...prev, [k]: v })),
    speak,
    stopSpeech,
    speaking,
    sessionId,
    setSessionId,
    tokenNumber,
    setTokenNumber,
    ocrResult,
    setOcrResult,
    aiSummary,
    setAiSummary,
    x402Tx,
    setX402Tx,
  };

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}
