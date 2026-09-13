import { useEffect, useRef, useState } from "react";
import {
  ArrowLeft,
  BellRing,
  Clock,
  Home,
  Languages,
  LifeBuoy,
  Monitor,
  PhoneCall,
  Smartphone,
  Volume2,
  VolumeX,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import {
  INTERVIEW_STEPS,
  SCREENS,
  SCREEN_TITLES,
  useKiosk,
  type ScreenId,
} from "./context";

const IDLE_LIMIT = 60;
const WARN_AT = 15;

export function DemoBar() {
  const k = useKiosk();
  return (
    <div className="sticky top-0 z-50 border-b border-border bg-card/95 backdrop-blur">
      <div className="mx-auto flex max-w-[1600px] flex-col gap-2 px-4 py-3">
        <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-3 sm:flex sm:flex-wrap sm:justify-between">
          <div className="flex min-w-0 items-center gap-3">
            <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-primary text-primary-foreground font-bold">
              M
            </div>
            <div className="min-w-0">
              <p className="truncate text-sm font-bold">MediKiosk Demo Console</p>
              <p className="truncate text-xs text-muted-foreground">
                AIIA · Ministry of AYUSH · SIH 2026 PS-4
              </p>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Button
              size="sm"
              variant={k.ayushMode ? "default" : "outline"}
              onClick={() => k.setAyushMode(!k.ayushMode)}
            >
              AYUSH mode {k.ayushMode ? "ON" : "OFF"}
            </Button>
            <Button
              size="sm"
              variant={k.screen === "doctor" ? "default" : "secondary"}
              onClick={() => k.go("doctor")}
            >
              Doctor Desk
            </Button>
            <Button size="sm" variant="outline" onClick={() => k.setKioskFrame(!k.kioskFrame)}>
              {k.kioskFrame ? <Smartphone className="mr-1 h-4 w-4" /> : <Monitor className="mr-1 h-4 w-4" />}
              {k.kioskFrame ? "Kiosk portrait" : "Fullscreen"}
            </Button>
            <Button size="sm" variant="destructive" onClick={() => k.go("emergency")}>
              <BellRing className="mr-1 h-4 w-4" /> Trigger red flag
            </Button>
          </div>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {SCREENS.map((s, i) => (
            <button
              key={s}
              onClick={() => k.go(s)}
              className={cn(
                "rounded-full border px-3 py-1 text-xs font-medium transition-colors",
                k.screen === s
                  ? "border-primary bg-primary text-primary-foreground"
                  : "border-border bg-background text-muted-foreground hover:bg-secondary",
              )}
            >
              {i + 1}. {SCREEN_TITLES[s]}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

function useClock() {
  const [now, setNow] = useState<Date | null>(null);
  useEffect(() => {
    setNow(new Date());
    const t = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(t);
  }, []);
  return now;
}

function Progress() {
  const k = useKiosk();
  const steps = INTERVIEW_STEPS.filter((s) => k.ayushMode || s !== "ayush");
  const idx = steps.indexOf(k.screen as ScreenId);
  if (idx < 0) return null;
  return (
    <div className="flex items-center gap-2 px-5 pb-2">
      {steps.map((s, i) => (
        <div
          key={s}
          className={cn(
            "h-2 flex-1 rounded-full",
            i <= idx ? "bg-success" : "bg-border",
          )}
        />
      ))}
      <span className="shrink-0 text-xs font-semibold text-muted-foreground">
        Step {idx + 1}/{steps.length}
      </span>
    </div>
  );
}

export function KioskShell({ children }: { children: React.ReactNode }) {
  const k = useKiosk();
  const now = useClock();
  const [help, setHelp] = useState(false);
  const [idle, setIdle] = useState(IDLE_LIMIT);
  const screenRef = useRef(k.screen);
  screenRef.current = k.screen;

  useEffect(() => setIdle(IDLE_LIMIT), [k.screen]);

  useEffect(() => {
    const reset = () => setIdle(IDLE_LIMIT);
    window.addEventListener("pointerdown", reset);
    window.addEventListener("keydown", reset);
    const t = setInterval(() => {
      setIdle((v) => {
        if (screenRef.current === "welcome") return IDLE_LIMIT;
        if (v <= 1) {
          k.restart();
          return IDLE_LIMIT;
        }
        return v - 1;
      });
    }, 1000);
    return () => {
      clearInterval(t);
      window.removeEventListener("pointerdown", reset);
      window.removeEventListener("keydown", reset);
    };
  }, [k]);

  const body = (
    <div
      className={cn(
        "flex h-full w-full flex-col bg-background text-foreground",
        k.highContrast && "hc",
        k.largeText && "text-[1.15em]",
      )}
    >
      <header className="flex items-center justify-between gap-3 border-b border-border bg-card px-5 py-3">
        <div className="flex min-w-0 items-center gap-2">
          <Button size="lg" variant="outline" className="h-16 px-4" onClick={k.back}>
            <ArrowLeft className="h-6 w-6" />
          </Button>
          <Button size="lg" variant="outline" className="h-16 px-4" onClick={k.restart}>
            <Home className="h-6 w-6" />
          </Button>
        </div>
        <div className="min-w-0 text-center">
          <p className="truncate text-lg font-bold">{SCREEN_TITLES[k.screen]}</p>
          <p className="flex items-center justify-center gap-1 text-xs text-muted-foreground">
            <Clock className="h-3 w-3" />
            {now ? now.toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "medium" }) : "--"}
          </p>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          <button
            onClick={() => k.go("language")}
            className="flex h-16 items-center gap-1 rounded-full border border-border px-4 text-base font-semibold"
          >
            <Languages className="h-5 w-5" /> {k.lang.native}
          </button>
          <Button
            size="lg"
            variant={k.speaking ? "default" : "outline"}
            className="h-16 px-4"
            onClick={() => (k.speaking ? k.stopSpeech() : k.speak(readoutFor(k.screen)))}
          >
            {k.speaking ? <VolumeX className="h-6 w-6" /> : <Volume2 className="h-6 w-6" />}
          </Button>
          <Button size="lg" className="h-16 px-4" variant="secondary" onClick={() => setHelp(true)}>
            <LifeBuoy className="mr-1 h-6 w-6" /> Help
          </Button>
        </div>
      </header>

      <Progress />

      <main className="flex-1 overflow-y-auto">{children}</main>

      <footer className="flex flex-wrap items-center justify-between gap-2 border-t border-border bg-card px-5 py-3 text-sm">
        <span className="font-semibold text-muted-foreground">
          All India Institute of Ayurveda · OPD Self-Check-In
        </span>
        <span className="flex items-center gap-2 font-bold text-destructive">
          <PhoneCall className="h-4 w-4" /> Emergency helpline 108 · Staff desk 1800-11-2233
        </span>
      </footer>

      <Dialog open={help} onOpenChange={setHelp}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="text-2xl">Staff has been called</DialogTitle>
          </DialogHeader>
          <p className="text-lg">
            A help desk attendant is on the way to Kiosk 3. Please wait here — average response time
            is under 60 seconds.
          </p>
          <Button size="lg" className="h-14 text-lg" onClick={() => setHelp(false)}>
            Okay, continue
          </Button>
        </DialogContent>
      </Dialog>

      <Dialog open={idle <= WARN_AT && k.screen !== "welcome"} onOpenChange={() => setIdle(IDLE_LIMIT)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="text-2xl">Still there? / अभी भी यहाँ हैं?</DialogTitle>
          </DialogHeader>
          <p className="text-lg">
            For your privacy this session will clear in <b>{idle}s</b> and return to the welcome
            screen.
          </p>
          <div className="flex gap-3">
            <Button size="lg" className="h-14 flex-1 text-lg" onClick={() => setIdle(IDLE_LIMIT)}>
              I&apos;m still here
            </Button>
            <Button size="lg" variant="outline" className="h-14 flex-1 text-lg" onClick={k.restart}>
              Finish session
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );

  if (!k.kioskFrame) return <div className="min-h-[80vh]">{body}</div>;

  return (
    <div className="flex justify-center bg-muted/50 p-6">
      <div
        className="w-full max-w-[560px] rounded-[2.5rem] border-[14px] border-slate-800 bg-slate-800 shadow-[var(--shadow-kiosk)]"
        style={{ aspectRatio: "9 / 16" }}
      >
        <div className="h-full w-full overflow-hidden rounded-[1.5rem]">{body}</div>
      </div>
    </div>
  );
}

export function readoutFor(screen: ScreenId): string {
  const map: Record<ScreenId, string> = {
    welcome: "Welcome to the All India Institute of Ayurveda. Touch the screen to start your OPD check in.",
    language: "Please choose your preferred language by touching a tile.",
    identify: "Identify yourself. Scan your ABHA QR code, type your ABHA or Aadhaar number, or register as a new patient.",
    consent: "Under the Digital Personal Data Protection Act, please give consent for voice recording, document scanning, and sharing with your doctor.",
    accessibility: "You can turn on high contrast, larger text, audio guidance, or a sign language assistant.",
    complaint: "Please tell us your main health problem. Press the microphone and speak, or tap a symptom card.",
    socrates: "A few quick questions about your pain: when it started, how severe it is, and where it hurts.",
    ayush: "Now a short Ayurvedic assessment, called Dashavidha Pariksha, about your body type, digestion, sleep, diet, strength and mind.",
    emergency: "Warning signs detected. Hospital staff have been alerted and a nurse is on the way. Please stay seated.",
    scan: "Place your prescription or report inside the guide box and press capture.",
    review: "Please check the details we read from your documents and approve them.",
    summary: "Here is a summary of everything you told us. Confirm if it is correct.",
    token: "Your check in is complete. Please collect your token and wait to be called.",
    reset: "Your personal data has been cleared from this kiosk. Thank you.",
    dashboard: "This is your patient companion app with your visit history and care plan.",
    doctor: "Doctor consultation and review portal.",
  };
  return map[screen] || "";
}
