import { useEffect, useMemo, useRef, useState } from "react";
import {
  Activity,
  AlertTriangle,
  Apple,
  BadgeCheck,
  Brain,
  Camera,
  Check,
  CheckCheck,
  CreditCard,
  Delete,
  Download,
  Dumbbell,
  FileText,
  FileScan,
  Flame,
  HeartPulse,
  Mic,
  Moon,
  Printer,
  QrCode,
  RefreshCw,
  ScanLine,
  Shield,
  Sparkles,
  Stethoscope,
  Thermometer,
  UserPlus,
  Volume2,
  ExternalLink,
  UploadCloud,
  CheckCircle2,
  Loader2,
  Lock,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { LANGUAGES, useKiosk } from "./context";
import { readoutFor } from "./shell";
import { api } from "@/lib/api";
const readoutSafe = readoutFor;

/* ---------- shared bits ---------- */

function Page({
  title,
  subtitle,
  children,
  footer,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
}) {
  return (
    <div className="flex min-h-full flex-col gap-5 p-6">
      <div>
        <h1 className="text-3xl font-extrabold leading-tight">{title}</h1>
        {subtitle ? <p className="mt-1 text-lg text-muted-foreground">{subtitle}</p> : null}
      </div>
      <div className="flex-1 space-y-4">{children}</div>
      {footer ? <div className="pt-2">{footer}</div> : null}
    </div>
  );
}

function BigButton({
  children,
  onClick,
  variant = "default",
  className,
}: {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: "default" | "outline" | "secondary" | "destructive";
  className?: string;
}) {
  return (
    <Button
      size="lg"
      variant={variant}
      onClick={onClick}
      className={cn("h-16 w-full rounded-2xl text-xl font-bold", className)}
    >
      {children}
    </Button>
  );
}

/* ---------- 1 Welcome ---------- */

function Welcome() {
  const k = useKiosk();
  const [i, setI] = useState(0);
  const [tokens, setTokens] = useState(103);
  useEffect(() => {
    const t = setInterval(() => setI((v) => (v + 1) % LANGUAGES.length), 1800);
    const t2 = setInterval(() => setTokens((v) => v + 1), 9000);
    return () => {
      clearInterval(t);
      clearInterval(t2);
    };
  }, []);
  const lang = LANGUAGES[i]!;
  return (
    <button
      onClick={() => k.go("language")}
      className="flex h-full w-full flex-col items-center justify-center gap-8 p-8 text-center"
      style={{ background: "var(--gradient-primary)" }}
    >
      <div className="flex items-center gap-3 rounded-full bg-white/15 px-5 py-2 text-primary-foreground">
        <Sparkles className="h-5 w-5" />
        <span className="text-sm font-bold tracking-wide">AIIA · MINISTRY OF AYUSH</span>
      </div>
      <div>
        <h1 className="text-5xl font-black text-primary-foreground">MediKiosk</h1>
        <p className="mt-2 text-xl text-primary-foreground/85">
          OPD Self Check-In · स्वयं पंजीकरण
        </p>
      </div>
      <div className="relative grid h-48 w-48 place-items-center">
        <span className="absolute h-40 w-40 rounded-full bg-white/40 pulse-ring" />
        <span className="grid h-40 w-40 place-items-center rounded-full bg-white/95 text-primary shadow-xl">
          <HeartPulse className="h-20 w-20" />
        </span>
      </div>
      <p className="min-h-[3rem] text-3xl font-extrabold text-primary-foreground">
        {lang.touchToStart}
      </p>
      <div className="rounded-2xl bg-white/15 px-6 py-3 text-primary-foreground">
        <p className="text-sm uppercase tracking-wide">Now serving token</p>
        <p className="text-4xl font-black">OPD-AYUSH-{tokens}</p>
      </div>
    </button>
  );
}

/* ---------- 2 Language ---------- */

function LanguageScreen() {
  const k = useKiosk();
  const [picked, setPicked] = useState<string | null>(null);
  return (
    <Page title="Choose your language" subtitle="अपनी भाषा चुनें">
      <div className="grid grid-cols-2 gap-4">
        {LANGUAGES.map((l) => (
          <button
            key={l.code}
            onClick={() => {
              k.setLang(l);
              setPicked(l.code);
              k.speak(`${l.greeting}`);
            }}
            className={cn(
              "min-h-[104px] rounded-2xl border-2 p-4 text-left transition-colors",
              picked === l.code
                ? "border-success bg-success/10"
                : "border-border bg-card hover:bg-secondary",
            )}
          >
            <p className="text-3xl font-black">{l.native}</p>
            <p className="text-base text-muted-foreground">
              {l.label} · {l.greeting}
            </p>
          </button>
        ))}
      </div>
      <p className="flex items-center gap-2 text-base text-muted-foreground">
        <Volume2 className="h-5 w-5" /> Tap a tile to hear the greeting spoken aloud.
      </p>
      <BigButton onClick={k.next} className="bg-success text-success-foreground">
        Confirm {k.lang.native} <Check className="ml-2 h-6 w-6" />
      </BigButton>
    </Page>
  );
}

/* ---------- 3 Identify ---------- */

function Keypad({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  const keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "clear", "0", "del"];
  return (
    <div className="grid grid-cols-3 gap-3">
      {keys.map((key) => (
        <button
          key={key}
          onClick={() =>
            key === "del"
              ? onChange(value.slice(0, -1))
              : key === "clear"
                ? onChange("")
                : onChange((value + key).slice(0, 14))
          }
          className="h-16 rounded-2xl border-2 border-border bg-card text-2xl font-bold hover:bg-secondary"
        >
          {key === "del" ? <Delete className="mx-auto h-6 w-6" /> : key === "clear" ? "C" : key}
        </button>
      ))}
    </div>
  );
}

function Identify() {
  const k = useKiosk();
  const [mode, setMode] = useState<"pick" | "qr" | "num" | "new">("pick");
  const [num, setNum] = useState("");
  const [scanned, setScanned] = useState(false);

  useEffect(() => {
    if (mode !== "qr") return;
    const t = setTimeout(() => setScanned(true), 2600);
    return () => clearTimeout(t);
  }, [mode]);

  if (mode === "pick")
    return (
      <Page title="Identify yourself" subtitle="अपनी पहचान बताएं">
        {[
          { id: "qr", icon: QrCode, t: "Scan ABHA QR", s: "Hold your ABHA card to the camera" },
          { id: "num", icon: CreditCard, t: "Enter ABHA / Aadhaar", s: "Type your 14-digit number" },
          { id: "new", icon: UserPlus, t: "New Patient / Register", s: "First visit? Register here" },
        ].map((o) => (
          <button
            key={o.id}
            onClick={() => setMode(o.id as typeof mode)}
            className="flex w-full items-center gap-4 rounded-2xl border-2 border-border bg-card p-5 text-left hover:bg-secondary"
          >
            <span className="grid h-16 w-16 shrink-0 place-items-center rounded-2xl bg-primary text-primary-foreground">
              <o.icon className="h-8 w-8" />
            </span>
            <span className="min-w-0">
              <span className="block text-2xl font-bold">{o.t}</span>
              <span className="block text-base text-muted-foreground">{o.s}</span>
            </span>
          </button>
        ))}
      </Page>
    );

  if (mode === "qr")
    return (
      <Page title="Scan ABHA QR" subtitle="Hold the QR code inside the box">
        <div className="relative aspect-square w-full overflow-hidden rounded-2xl bg-slate-900">
          <div className="absolute inset-8 rounded-xl border-4 border-dashed border-white/70" />
          {!scanned && <div className="scanline absolute left-6 right-6 h-1 bg-success" />}
          {scanned && (
            <div className="absolute inset-0 grid place-items-center bg-success/85 text-success-foreground">
              <div className="text-center">
                <CheckCheck className="mx-auto h-20 w-20" />
                <p className="mt-2 text-2xl font-bold">ABHA verified</p>
                <p>{k.patient.name} · {k.patient.abha}</p>
              </div>
            </div>
          )}
        </div>
        <BigButton onClick={k.next} className="bg-success text-success-foreground">
          Continue
        </BigButton>
        <BigButton variant="outline" onClick={() => setMode("pick")}>
          Use another method
        </BigButton>
      </Page>
    );

  if (mode === "num")
    return (
      <Page title="Enter ABHA / Aadhaar" subtitle="14 or 12 digit number">
        <div className="rounded-2xl border-2 border-border bg-card p-4 text-center text-3xl font-black tracking-widest">
          {num || "— — — —"}
        </div>
        <Keypad value={num} onChange={setNum} />
        <BigButton
          onClick={() => {
            k.setPatient({ abha: num || k.patient.abha });
            k.next();
          }}
          className="bg-success text-success-foreground"
        >
          Verify &amp; Continue
        </BigButton>
        <BigButton variant="outline" onClick={() => setMode("pick")}>
          Back
        </BigButton>
      </Page>
    );

  return (
    <Page title="New patient registration" subtitle="नया पंजीकरण">
      {[
        { k: "name", l: "Full name / पूरा नाम" },
        { k: "age", l: "Age / आयु" },
        { k: "gender", l: "Gender / लिंग" },
        { k: "mobile", l: "Mobile number / मोबाइल" },
      ].map((f) => (
        <div key={f.k} className="space-y-1">
          <Label className="text-lg">{f.l}</Label>
          <Input
            className="h-16 rounded-2xl text-xl"
            value={(k.patient as Record<string, string>)[f.k] ?? ""}
            onChange={(e) => k.setPatient({ [f.k]: e.target.value })}
          />
        </div>
      ))}
      <BigButton onClick={k.next} className="bg-success text-success-foreground">
        Register &amp; Continue
      </BigButton>
      <BigButton variant="outline" onClick={() => setMode("pick")}>
        Back
      </BigButton>
    </Page>
  );
}

/* ---------- 4 Consent ---------- */

function Consent() {
  const k = useKiosk();
  const items = [
    { id: "voice", t: "Voice recording", s: "Record what you say to fill your case sheet" },
    { id: "docs", t: "Document scanning", s: "Scan prescriptions and lab reports" },
    { id: "share", t: "Share with Doctor / ABHA", s: "Send this record to your doctor and ABHA locker" },
  ];
  const [on, setOn] = useState<Record<string, boolean>>({ voice: true, docs: true, share: true });
  const [declined, setDeclined] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleAgree = async () => {
    setIsSubmitting(true);
    try {
      const sess = await api.createSession({
        name: k.patient.name,
        age: parseInt(k.patient.age, 10) || 42,
        gender: k.patient.gender,
        mobile: k.patient.mobile,
        abha_id: k.patient.abha,
        language: k.lang.code,
      });
      if (sess && sess.session_id) {
        k.setSessionId(sess.session_id);
        if (sess.token_number) k.setTokenNumber(sess.token_number);
      }
    } catch (e) {
      console.warn("Session create error:", e);
    } finally {
      setIsSubmitting(false);
      k.next();
    }
  };

  if (declined)
    return (
      <Page title="Please visit the staff desk" subtitle="Counter 2, to your left">
        <Card className="border-warning bg-warning/15 p-6 text-xl font-semibold">
          Without digital consent we cannot record your details here. A staff member will complete
          your registration manually.
        </Card>
        <BigButton onClick={k.restart}>Return to start</BigButton>
      </Page>
    );

  return (
    <Page
      title="Your data, your choice"
      subtitle="Digital Personal Data Protection Act, 2023 · डिजिटल सहमति"
    >
      {items.map((i) => (
        <div
          key={i.id}
          className="flex items-center justify-between gap-4 rounded-2xl border-2 border-border bg-card p-5"
        >
          <div className="min-w-0">
            <p className="text-xl font-bold">{i.t}</p>
            <p className="text-base text-muted-foreground">{i.s}</p>
          </div>
          <Switch
            className="scale-150"
            checked={!!on[i.id]}
            onCheckedChange={(v) => setOn((p) => ({ ...p, [i.id]: v }))}
          />
        </div>
      ))}
      <Button
        variant="outline"
        className="h-14 w-full rounded-2xl text-lg"
        onClick={() => k.speak(readoutFor("consent"))}
      >
        <Volume2 className="mr-2 h-5 w-5" /> Read this aloud
      </Button>
      <BigButton className="bg-success text-success-foreground" onClick={handleAgree}>
        {isSubmitting ? (
          <><Loader2 className="mr-2 h-6 w-6 animate-spin" /> Starting session…</>
        ) : (
          <><Shield className="mr-2 h-6 w-6" /> I agree</>
        )}
      </BigButton>
      <BigButton variant="outline" onClick={() => setDeclined(true)}>
        I decline
      </BigButton>
    </Page>
  );
}

/* ---------- 5 Accessibility ---------- */

function Accessibility() {
  const k = useKiosk();
  const rows = [
    { t: "High contrast", s: "Stronger colours for low vision", v: k.highContrast, set: k.setHighContrast },
    { t: "Large text", s: "Bigger letters everywhere", v: k.largeText, set: k.setLargeText },
    { t: "Audio-guided mode", s: "Read every screen aloud automatically", v: k.autoRead, set: k.setAutoRead },
    { t: "Sign language assistant", s: "Show an avatar signing the questions", v: k.signAvatar, set: k.setSignAvatar },
  ];
  return (
    <Page title="Make it easier for you" subtitle="You can skip this step">
      {rows.map((r) => (
        <div
          key={r.t}
          className="flex items-center justify-between gap-4 rounded-2xl border-2 border-border bg-card p-5"
        >
          <div className="min-w-0">
            <p className="text-xl font-bold">{r.t}</p>
            <p className="text-base text-muted-foreground">{r.s}</p>
          </div>
          <Switch className="scale-150" checked={r.v} onCheckedChange={r.set} />
        </div>
      ))}
      {k.signAvatar && (
        <Card className="grid place-items-center gap-2 bg-secondary p-6 text-center">
          <div className="grid h-28 w-28 animate-pulse place-items-center rounded-full bg-primary text-primary-foreground text-4xl">
            🤟
          </div>
          <p className="text-lg font-semibold">Sign language avatar preview (ISL)</p>
        </Card>
      )}
      <BigButton className="bg-success text-success-foreground" onClick={k.next}>
        Continue
      </BigButton>
      <BigButton variant="outline" onClick={k.next}>
        Skip
      </BigButton>
    </Page>
  );
}

/* ---------- 6 Chief complaint ---------- */

const SYMPTOMS = [
  { t: "Fever", h: "बुखार", icon: Thermometer },
  { t: "Abdominal pain", h: "पेट दर्द", icon: Activity },
  { t: "Cough / Breathing", h: "खांसी", icon: Stethoscope },
  { t: "Joint / Body ache", h: "जोड़ों का दर्द", icon: Dumbbell },
  { t: "Skin issue", h: "त्वचा", icon: Sparkles },
  { t: "Other", h: "अन्य", icon: FileText },
];

function Complaint() {
  const k = useKiosk();
  const [listening, setListening] = useState(false);
  const [text, setText] = useState(k.complaint);
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);
  const demo =
    "I have been having fever and body ache since three days, with mild stomach pain after meals.";

  useEffect(() => () => { if (timer.current) clearInterval(timer.current); }, []);

  const toggle = () => {
    if (listening) {
      setListening(false);
      if (timer.current) clearInterval(timer.current);
      return;
    }
    setListening(true);
    setText("");
    let i = 0;
    timer.current = setInterval(() => {
      i += 2;
      setText(demo.slice(0, i));
      if (i >= demo.length) {
        if (timer.current) clearInterval(timer.current);
        setListening(false);
        k.setComplaint(demo);
      }
    }, 45);
  };

  return (
    <Page title="What brings you today?" subtitle="आज आपको क्या तकलीफ है?">
      <div className="grid place-items-center gap-3 py-2">
        <button onClick={toggle} className="relative grid h-40 w-40 place-items-center">
          {listening && <span className="absolute h-36 w-36 rounded-full bg-destructive/40 pulse-ring" />}
          <span
            className={cn(
              "grid h-36 w-36 place-items-center rounded-full text-primary-foreground shadow-lg",
              listening ? "bg-destructive" : "bg-primary",
            )}
          >
            <Mic className="h-16 w-16" />
          </span>
        </button>
        <p className="text-lg font-semibold text-muted-foreground">
          {listening ? "Listening… बोलिए" : "Tap and speak"}
        </p>
      </div>
      <Card className="min-h-[104px] p-4 text-xl">
        {text || <span className="text-muted-foreground">Your words will appear here…</span>}
        {listening && <span className="ml-1 animate-pulse">▌</span>}
      </Card>
      <div className="grid grid-cols-2 gap-3">
        {SYMPTOMS.map((s) => (
          <button
            key={s.t}
            onClick={() => {
              setText(s.t);
              k.setComplaint(s.t);
            }}
            className={cn(
              "min-h-[96px] rounded-2xl border-2 p-3 text-left",
              text === s.t ? "border-success bg-success/10" : "border-border bg-card",
            )}
          >
            <s.icon className="h-7 w-7 text-primary" />
            <p className="mt-1 text-lg font-bold leading-tight">{s.t}</p>
            <p className="text-sm text-muted-foreground">{s.h}</p>
          </button>
        ))}
      </div>
      <BigButton
        className="bg-success text-success-foreground"
        onClick={async () => {
          const complaintText = text || "Fever and body ache";
          k.setComplaint(complaintText);
          if (k.sessionId) {
            api.submitAnswers(k.sessionId, [
              { question_id: "chief_complaint", question_text: "What brings you today?", answer_text: complaintText },
            ]);
          }
          // Red-flag detection for emergency triage
          if (
            complaintText.toLowerCase().includes("chest pain") &&
            (complaintText.toLowerCase().includes("breath") || complaintText.toLowerCase().includes("shortness"))
          ) {
            k.go("emergency");
          } else {
            k.next();
          }
        }}
      >
        Continue
      </BigButton>
    </Page>
  );
}

/* ---------- 7 SOCRATES ---------- */

function Socrates() {
  const k = useKiosk();
  const [side, setSide] = useState<"front" | "back">("front");
  const chips = ["Burning", "Cramping", "Sharp", "Dull ache", "Throbbing"];
  const onsets = ["Today", "2–3 days", "1 week", "1 month+"];
  const aggr = ["After food", "At night", "On movement", "Cold weather", "Stress"];
  const regions = ["Head", "Chest", "Abdomen", "Lower back", "Knees", "Feet"];

  return (
    <Page title="Tell us a bit more" subtitle="कुछ और जानकारी दें">
      <section className="space-y-2">
        <p className="text-xl font-bold">When did it start? (Onset)</p>
        <div className="flex flex-wrap gap-2">
          {onsets.map((o) => (
            <Chip key={o} active={k.answers["onset"] === o} onClick={() => k.setAnswer("onset", o)}>
              {o}
            </Chip>
          ))}
        </div>
      </section>

      <section className="space-y-3">
        <p className="text-xl font-bold">How bad is the pain? {k.severity}/10</p>
        <Slider value={[k.severity]} min={0} max={10} step={1} onValueChange={(v) => k.setSeverity(v[0] ?? 5)} />
        <div className="flex justify-between text-base text-muted-foreground">
          <span>😊 No pain</span>
          <span>😣 Worst</span>
        </div>
      </section>

      <section className="space-y-2">
        <div className="flex items-center justify-between">
          <p className="text-xl font-bold">Where does it hurt?</p>
          <Button variant="outline" onClick={() => setSide(side === "front" ? "back" : "front")}>
            <RefreshCw className="mr-1 h-4 w-4" /> {side === "front" ? "Front" : "Back"}
          </Button>
        </div>
        <div className="grid grid-cols-3 gap-2">
          {regions.map((r) => (
            <Chip
              key={r}
              active={k.answers["region"] === `${r} (${side})`}
              onClick={() => k.setAnswer("region", `${r} (${side})`)}
            >
              {r}
            </Chip>
          ))}
        </div>
      </section>

      <section className="space-y-2">
        <p className="text-xl font-bold">Nature of pain</p>
        <div className="flex flex-wrap gap-2">
          {chips.map((c) => (
            <Chip key={c} active={k.answers["nature"] === c} onClick={() => k.setAnswer("nature", c)}>
              {c}
            </Chip>
          ))}
        </div>
      </section>

      <section className="space-y-2">
        <p className="text-xl font-bold">What makes it worse?</p>
        <div className="flex flex-wrap gap-2">
          {aggr.map((a) => (
            <Chip key={a} active={k.answers["aggravating"] === a} onClick={() => k.setAnswer("aggravating", a)}>
              {a}
            </Chip>
          ))}
        </div>
      </section>

      <BigButton
        className="bg-success text-success-foreground"
        onClick={async () => {
          if (k.sessionId) {
            const list = Object.entries(k.answers).map(([key, val]) => ({
              question_id: key,
              question_text: key,
              answer_text: val,
            }));
            list.push({ question_id: "severity", question_text: "Pain severity", answer_text: `${k.severity}/10` });
            api.submitAnswers(k.sessionId, list);
          }
          k.next();
        }}
      >
        Continue
      </BigButton>
      <BigButton variant="outline" onClick={k.next}>
        I don&apos;t know / Skip
      </BigButton>
    </Page>
  );
}

function Chip({
  children,
  active,
  onClick,
}: {
  children: React.ReactNode;
  active?: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "min-h-[64px] rounded-2xl border-2 px-5 text-lg font-semibold",
        active ? "border-success bg-success/10" : "border-border bg-card",
      )}
    >
      {children}
    </button>
  );
}

/* ---------- 8 AYUSH ---------- */

function Ayush() {
  const k = useKiosk();
  const blocks = [
    { id: "prakriti", icon: Brain, t: "Prakriti / शरीर प्रकृति", s: "Your natural body type", opts: ["Vata (dry, active)", "Pitta (warm, sharp)", "Kapha (calm, heavy)"] },
    { id: "agni", icon: Flame, t: "Agni / पाचन", s: "How is your digestion?", opts: ["Strong", "Irregular", "Weak"] },
    { id: "nidra", icon: Moon, t: "Nidra / नींद", s: "How do you sleep?", opts: ["Sound sleep", "Broken sleep", "Very little"] },
    { id: "ahara", icon: Apple, t: "Ahara / आहार", s: "Your usual food", opts: ["Vegetarian", "Mixed", "Mostly outside food"] },
    { id: "bala", icon: Dumbbell, t: "Bala / शक्ति", s: "Your daily strength", opts: ["Good", "Average", "Weak"] },
    { id: "satva", icon: HeartPulse, t: "Satva / मन", s: "Your mental state", opts: ["Calm", "Worried", "Very stressed"] },
  ];
  if (!k.ayushMode)
    return (
      <Page title="AYUSH history is off" subtitle="Turn on AYUSH mode in the demo bar to see Dashavidha Pariksha">
        <BigButton onClick={k.next}>Continue</BigButton>
      </Page>
    );
  return (
    <Page title="Ayurvedic assessment" subtitle="दशविध परीक्षा · Dashavidha Pariksha">
      {blocks.map((b) => (
        <Card key={b.id} className="space-y-3 p-4">
          <div className="flex items-center gap-3">
            <span className="grid h-12 w-12 shrink-0 place-items-center rounded-xl bg-accent text-accent-foreground">
              <b.icon className="h-6 w-6" />
            </span>
            <div className="min-w-0">
              <p className="text-xl font-bold">{b.t}</p>
              <p className="text-base text-muted-foreground">{b.s}</p>
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            {b.opts.map((o) => (
              <Chip key={o} active={k.answers[b.id] === o} onClick={() => k.setAnswer(b.id, o)}>
                {o}
              </Chip>
            ))}
          </div>
        </Card>
      ))}
      <BigButton className="bg-success text-success-foreground" onClick={k.next}>
        Continue
      </BigButton>
    </Page>
  );
}

/* ---------- 9 Emergency ---------- */

function Emergency() {
  const k = useKiosk();
  return (
    <div className="flex min-h-full flex-col items-center justify-center gap-6 bg-destructive p-8 text-center text-destructive-foreground">
      <AlertTriangle className="beacon h-28 w-28" />
      <h1 className="text-4xl font-black">Hospital staff alerted</h1>
      <p className="text-2xl font-semibold">A nurse is on the way to Kiosk 3.</p>
      <div className="rounded-2xl bg-white/20 px-8 py-5">
        <p className="text-sm uppercase tracking-widest">Emergency token</p>
        <p className="text-5xl font-black">EMG-07</p>
      </div>
      <p className="max-w-md text-xl">
        Please stay seated and breathe slowly. You are safe — help arrives in under 2 minutes.
      </p>
      <div className="w-full max-w-sm space-y-3">
        <BigButton variant="secondary" onClick={() => k.speak("Hospital staff have been alerted. A nurse is on the way. Please stay seated.")}>
          <Volume2 className="mr-2 h-6 w-6" /> Play reassurance
        </BigButton>
        <BigButton variant="outline" className="bg-white/10" onClick={() => k.go("complaint")}>
          Resume check-in
        </BigButton>
      </div>
    </div>
  );
}

/* ---------- 10 Scan ---------- */

function Scan() {
  const k = useKiosk();
  const [pages, setPages] = useState<string[]>([]);
  const [flash, setFlash] = useState(false);
  const [ocr, setOcr] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setFlash(true);
    setTimeout(() => setFlash(false), 200);
    setPages((p) => [...p, file.name]);
    setOcr(10);
    setIsUploading(true);

    const timer = setInterval(() => {
      setOcr((v) => (v < 85 ? v + 15 : v));
    }, 150);

    try {
      const activeSession = k.sessionId || "demo-session-1";
      const doc = await api.uploadDocument(activeSession, file, "prescription");
      clearInterval(timer);
      setOcr(100);
      k.setOcrResult(doc);
    } catch (err) {
      console.warn("Upload error:", err);
      clearInterval(timer);
      setOcr(100);
    } finally {
      setIsUploading(false);
    }
  };

  const simulateCapture = async () => {
    setFlash(true);
    setTimeout(() => setFlash(false), 200);
    const newPage = `Page ${pages.length + 1}.jpg`;
    setPages((p) => [...p, newPage]);
    setOcr(20);
    setIsUploading(true);

    const timer = setInterval(() => {
      setOcr((v) => (v < 90 ? v + 12 : v));
    }, 120);

    try {
      const activeSession = k.sessionId || "demo-session-1";
      const fakeBlob = new Blob(["Prescription OCR Demo"], { type: "image/jpeg" });
      const fakeFile = new File([fakeBlob], newPage, { type: "image/jpeg" });
      const doc = await api.uploadDocument(activeSession, fakeFile, "prescription");
      clearInterval(timer);
      setOcr(100);
      k.setOcrResult(doc);
    } catch {
      clearInterval(timer);
      setOcr(100);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Page title="Scan your documents" subtitle="पर्ची या रिपोर्ट स्कैन करें">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileUpload}
        className="hidden"
        accept="image/*,application/pdf"
      />
      <div className="relative aspect-[4/3] w-full overflow-hidden rounded-2xl bg-slate-900 flex items-center justify-center">
        <div className="absolute inset-6 rounded-lg border-4 border-dashed border-success/80" />
        <p className="absolute bottom-3 left-0 right-0 text-center text-white/80">
          Align the paper inside the green guide or upload a prescription
        </p>
        <UploadCloud className="h-20 w-20 text-white/20" />
        {flash && <div className="absolute inset-0 bg-white" />}
      </div>
      <div className="grid grid-cols-2 gap-3">
        <BigButton onClick={simulateCapture} disabled={isUploading}>
          <Camera className="mr-2 h-6 w-6" /> Capture
        </BigButton>
        <BigButton variant="outline" onClick={() => fileInputRef.current?.click()} disabled={isUploading}>
          <UploadCloud className="mr-2 h-6 w-6" /> Upload File
        </BigButton>
      </div>

      <div className="space-y-2 pt-2">
        <p className="text-sm font-semibold text-muted-foreground">Or test with verified clinical prescriptions:</p>
        <div className="grid grid-cols-2 gap-2">
          <Button
            variant="secondary"
            size="sm"
            className="h-auto py-2 px-3 text-left flex flex-col items-start"
            onClick={() => {
              const text = "AIIA AYUSH OPD. Dr. Rajesh Sharma. Date: 12 Aug 2026. Rx: 1. Tab. Arogyavardhini Vati 250mg BD, 2. Tab. Paracetamol 500mg SOS. Vitals: Hb 9.1 g/dL, Fasting glucose 148 mg/dL, BP 130/85 mmHg.";
              const fakeBlob = new Blob([text], { type: "text/plain" });
              const fakeFile = new File([fakeBlob], "AYUSH_OPD_Prescription.txt", { type: "text/plain" });
              setPages(["AYUSH_OPD_Prescription.jpg"]);
              setOcr(100);
              k.setOcrResult({
                document_id: "doc-ayush-1",
                session_id: k.sessionId || "demo",
                document_type: "prescription",
                ocr_text: text,
                entities: {
                  medicines: ["Tab. Arogyavardhini Vati 250mg", "Tab. Paracetamol 500mg"],
                  dates: ["12 Aug 2026"],
                  vitals: { haemoglobin: "9.1 g/dL", fasting_glucose: "148 mg/dL", blood_pressure: "130/85 mmHg" },
                  doctor: "Dr. Rajesh Sharma",
                  hospital: "AIIA AYUSH OPD"
                },
                file_url: ""
              });
            }}
          >
            <span className="font-bold text-xs">🌿 AYUSH + Allopathy Rx</span>
            <span className="text-[11px] text-muted-foreground">Arogyavardhini + Hb 9.1</span>
          </Button>

          <Button
            variant="secondary"
            size="sm"
            className="h-auto py-2 px-3 text-left flex flex-col items-start"
            onClick={() => {
              const text = "City Care Cardiology Clinic. Dr. A. Verma. Date: 10-Sep-2026. Rx: 1. Tab. Metformin 500mg BD, 2. Tab. Atorvastatin 10mg HS, 3. Tab. Amlodipine 5mg OD. Vitals: BP 140/90 mmHg, Pulse 82 bpm, RBS 165 mg/dL.";
              const fakeBlob = new Blob([text], { type: "text/plain" });
              const fakeFile = new File([fakeBlob], "Cardiology_Prescription.txt", { type: "text/plain" });
              setPages(["Cardiology_Rx.jpg"]);
              setOcr(100);
              k.setOcrResult({
                document_id: "doc-cardio-1",
                session_id: k.sessionId || "demo",
                document_type: "prescription",
                ocr_text: text,
                entities: {
                  medicines: ["Tab. Metformin 500mg", "Tab. Atorvastatin 10mg", "Tab. Amlodipine 5mg"],
                  dates: ["10-Sep-2026"],
                  vitals: { blood_pressure: "140/90 mmHg", pulse: "82 bpm", random_glucose: "165 mg/dL" },
                  doctor: "Dr. A. Verma",
                  hospital: "City Care Cardiology Clinic"
                },
                file_url: ""
              });
            }}
          >
            <span className="font-bold text-xs">❤️ Cardiology &amp; Diabetes Rx</span>
            <span className="text-[11px] text-muted-foreground">Metformin + BP 140/90</span>
          </Button>
        </div>
      </div>
      {pages.length > 0 && (
        <>
          <div className="flex gap-3 overflow-x-auto pb-1">
            {pages.map((p) => (
              <div key={p} className="grid h-28 w-24 shrink-0 place-items-center rounded-xl border-2 border-border bg-card p-2 text-center text-xs truncate">
                <FileScan className="h-7 w-7 text-primary" />
                <span className="truncate w-full">{p}</span>
              </div>
            ))}
          </div>
          <Card className="space-y-2 p-4">
            <p className="flex items-center gap-2 text-lg font-bold">
              <ScanLine className="h-5 w-5" /> Reading text… {ocr}%
            </p>
            <div className="h-3 w-full overflow-hidden rounded-full bg-border">
              <div className="h-full rounded-full bg-success transition-all" style={{ width: `${ocr}%` }} />
            </div>
          </Card>
        </>
      )}
      <BigButton className="bg-success text-success-foreground" onClick={k.next} disabled={isUploading && ocr < 100}>
        Continue
      </BigButton>
    </Page>
  );
}

/* ---------- 11 Review ---------- */

function Review() {
  const k = useKiosk();
  const ocr = k.ocrResult;

  const fields = useMemo(() => {
    if (ocr && ocr.entities) {
      const items: { l: string; v: string; flag: boolean }[] = [];
      const ent = ocr.entities;

      if (ent.dates && ent.dates.length > 0) {
        items.push({ l: "Prescription date", v: ent.dates.join(", "), flag: false });
      }

      if (ent.medicines && ent.medicines.length > 0) {
        ent.medicines.forEach((m: string) => {
          items.push({ l: "Medicine extracted", v: m, flag: false });
        });
      }

      if (ent.vitals && Object.keys(ent.vitals).length > 0) {
        Object.entries(ent.vitals).forEach(([vk, vv]) => {
          const formattedKey = vk.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
          items.push({ l: formattedKey, v: String(vv), flag: true });
        });
      }

      if (ent.doctor) {
        items.push({ l: "Referring doctor", v: ent.doctor, flag: false });
      }
      if (ent.hospital) {
        items.push({ l: "Hospital / Clinic", v: ent.hospital, flag: false });
      }

      if (items.length > 0) return items;
    }

    return [
      { l: "Prescription date", v: "12 Aug 2026", flag: false },
      { l: "Medicine", v: "Tab. Arogyavardhini Vati 250mg", flag: false },
      { l: "Medicine", v: "Tab. Paracetamol 500mg (SOS)", flag: false },
      { l: "Haemoglobin", v: "9.1 g/dL (low)", flag: true },
      { l: "Fasting glucose", v: "148 mg/dL (high)", flag: true },
      { l: "Referring doctor", v: "Dr. R. Sharma", flag: false },
    ];
  }, [ocr]);
  return (
    <Page title="Check what we read" subtitle="Tap the tick if this is correct">
      <div className="grid gap-4 sm:grid-cols-2">
        <Card className="grid min-h-[220px] place-items-center bg-secondary p-4 text-center">
          <div>
            <FileText className="mx-auto h-16 w-16 text-primary" />
            <p className="mt-2 font-semibold">Scanned slip preview</p>
            <p className="text-sm text-muted-foreground">page 1 of {1}</p>
          </div>
        </Card>
        <div className="space-y-2">
          {fields.map((f, i) => (
            <div
              key={i}
              className={cn(
                "flex items-center justify-between gap-3 rounded-xl border-2 p-3",
                f.flag ? "border-warning bg-warning/15" : "border-border bg-card",
              )}
            >
              <div className="min-w-0">
                <p className="text-sm text-muted-foreground">{f.l}</p>
                <p className="truncate text-lg font-bold">{f.v}</p>
              </div>
              <Check className="h-6 w-6 shrink-0 text-success" />
            </div>
          ))}
        </div>
      </div>
      <BigButton className="bg-success text-success-foreground" onClick={k.next}>
        <BadgeCheck className="mr-2 h-6 w-6" /> All correct
      </BigButton>
    </Page>
  );
}

/* ---------- 12 Summary ---------- */

function Summary() {
  const k = useKiosk();
  const [loadingAi, setLoadingAi] = useState(false);

  useEffect(() => {
    // Automatically trigger AI clinical summary generation when reaching this screen
    if (k.sessionId && !k.aiSummary) {
      setLoadingAi(true);
      api
        .generateAiSummary(k.sessionId)
        .then((s) => {
          k.setAiSummary(s);
          setLoadingAi(false);
        })
        .catch(() => setLoadingAi(false));
    }
  }, [k.sessionId, k.aiSummary]);

  const rows = useMemo(
    () => [
      { l: "Patient", v: `${k.patient.name}, ${k.patient.age}, ${k.patient.gender}`, to: "identify" as const },
      { l: "Chief complaint", v: k.complaint || "Fever and body ache", to: "complaint" as const },
      { l: "Started", v: k.answers["onset"] ?? "2–3 days", to: "socrates" as const },
      { l: "Severity", v: `${k.severity}/10`, to: "socrates" as const },
      { l: "Pain type", v: k.answers["nature"] ?? "Dull ache", to: "socrates" as const },
      ...(k.ayushMode
        ? [{ l: "Prakriti / Agni", v: `${k.answers["prakriti"] ?? "Pitta"} · ${k.answers["agni"] ?? "Irregular"}`, to: "ayush" as const }]
        : []),
      { l: "Documents", v: k.ocrResult ? "1 prescription (OCR Verified)" : "1 prescription, 1 lab report", to: "scan" as const },
    ],
    [k],
  );

  const spoken = rows.map((r) => `${r.l}: ${r.v}`).join(". ");

  return (
    <Page title="Clinical Summary &amp; Review" subtitle="यह जानकारी आपके डॉक्टर को भेजी जाएगी">
      <Card className="divide-y divide-border p-0">
        {rows.map((r) => (
          <button
            key={r.l}
            onClick={() => k.go(r.to)}
            className="flex w-full items-center justify-between gap-3 p-4 text-left hover:bg-secondary"
          >
            <span className="min-w-0">
              <span className="block text-sm text-muted-foreground">{r.l}</span>
              <span className="block text-lg font-bold">{r.v}</span>
            </span>
            <span className="shrink-0 text-base font-semibold text-primary">Edit</span>
          </button>
        ))}
      </Card>

      {/* AI Structured Summary Section */}
      <Card className="p-4 border-2 border-primary/20 bg-primary/5 space-y-2">
        <div className="flex items-center justify-between">
          <p className="font-bold flex items-center gap-2 text-primary">
            <Sparkles className="h-5 w-5" /> AI Clinical Intake Preview
          </p>
          {loadingAi && <Loader2 className="h-4 w-4 animate-spin text-primary" />}
        </div>
        {loadingAi ? (
          <p className="text-sm text-muted-foreground animate-pulse">
            Generating AI clinical summary with Gemini &amp; ICD-11 classification…
          </p>
        ) : k.aiSummary ? (
          <div className="text-sm space-y-1">
            <p><strong>HPI:</strong> {k.aiSummary.hpi || "Patient reports fever and dull generalized body ache."}</p>
            <p><strong>Red Flags:</strong> <span className={k.aiSummary.red_flags_noted?.toLowerCase().includes("priority") || k.aiSummary.red_flags_noted?.toLowerCase().includes("alert") ? "text-destructive font-bold" : "text-success"}>{k.aiSummary.red_flags_noted || "None detected."}</span></p>
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">Clinical intake ready for doctor review.</p>
        )}
      </Card>

      <Button variant="outline" className="h-14 w-full rounded-2xl text-lg" onClick={() => k.speak(spoken)}>
        <Volume2 className="mr-2 h-5 w-5" /> Read my summary aloud
      </Button>
      <BigButton className="bg-success text-success-foreground" onClick={k.next}>
        Confirm &amp; Proceed to Token
      </BigButton>
    </Page>
  );
}

/* ---------- 13 Token & x402 Micropayment ---------- */

function Token() {
  const k = useKiosk();
  const [printed, setPrinted] = useState(false);
  const [paying, setPaying] = useState(false);

  const handleX402Pay = async () => {
    setPaying(true);
    try {
      const res = await api.verifyX402Payment(true);
      if (res && res.verification) {
        k.setX402Tx(res.verification);
      }
    } catch (err) {
      console.warn("x402 error:", err);
    } finally {
      setPaying(false);
    }
  };

  return (
    <Page title="You are checked in!" subtitle="आपका पंजीकरण पूरा हुआ">
      <div className="grid place-items-center gap-4 py-2">
        <div className="grid h-32 w-32 place-items-center rounded-full bg-success text-success-foreground">
          <Check className="h-20 w-20" />
        </div>
        <div className="rounded-2xl bg-primary px-8 py-5 text-center text-primary-foreground">
          <p className="text-sm uppercase tracking-widest">Your token</p>
          <p className="text-5xl font-black">{k.tokenNumber}</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <Card className="p-4">
          <p className="text-sm text-muted-foreground">Estimated wait</p>
          <p className="text-2xl font-bold">~18 minutes</p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-muted-foreground">Doctor / Cabin</p>
          <p className="text-2xl font-bold">Dr. Sharma · Room 12</p>
        </Card>
      </div>

      {/* x402 Algorand Micropayments Card */}
      <Card className="p-4 border-2 border-indigo-500/30 bg-indigo-50/50 dark:bg-indigo-950/20 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="grid h-8 w-8 place-items-center rounded-lg bg-indigo-600 text-white text-xs font-black">
              x402
            </span>
            <div>
              <p className="font-bold text-sm">Algorand TestNet Micropayment</p>
              <p className="text-xs text-muted-foreground">Facilitator: GoPlausible · 0.005 USDC</p>
            </div>
          </div>
          {k.x402Tx ? (
            <span className="flex items-center gap-1 text-xs font-bold text-success">
              <CheckCircle2 className="h-4 w-4" /> Settled
            </span>
          ) : (
            <span className="flex items-center gap-1 text-xs font-semibold text-amber-600 dark:text-amber-400">
              <Lock className="h-4 w-4" /> Challenge Ready
            </span>
          )}
        </div>

        {k.x402Tx ? (
          <div className="rounded-xl bg-background/80 p-3 space-y-1 text-xs border border-border">
            <p className="truncate"><strong>Tx ID:</strong> {k.x402Tx.tx_id}</p>
            <p><strong>Network:</strong> {k.x402Tx.network}</p>
            <a
              href={k.x402Tx.lora_url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 text-indigo-600 dark:text-indigo-400 font-bold hover:underline mt-1"
            >
              Verify on Lora Algokit Explorer <ExternalLink className="h-3 w-3" />
            </a>
          </div>
        ) : (
          <Button
            size="sm"
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold"
            onClick={handleX402Pay}
            disabled={paying}
          >
            {paying ? (
              <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Verifying with GoPlausible Facilitator…</>
            ) : (
              "Pay $0.005 via x402 Algorand"
            )}
          </Button>
        )}
      </Card>

      {printed && (
        <Card className="mx-auto w-full max-w-xs border-dashed p-4 text-center font-mono text-sm">
          <p className="font-bold">AIIA · OPD RECEIPT</p>
          <p>Token {k.tokenNumber}</p>
          <p>{k.patient.name} · {k.patient.age}</p>
          <p>Dr. Sharma · Room 12</p>
          {k.x402Tx && <p className="text-xs text-muted-foreground mt-1">x402 Algorand: Verified</p>}
          <p>Wait ~18 min</p>
          <p className="mt-2">— keep this slip —</p>
        </Card>
      )}

      <BigButton onClick={() => setPrinted(true)}>
        <Printer className="mr-2 h-6 w-6" /> Print token
      </BigButton>
      <BigButton className="bg-success text-success-foreground" onClick={k.next}>
        Done
      </BigButton>
    </Page>
  );
}

/* ---------- 14 Reset ---------- */

function ResetScreen() {
  const k = useKiosk();
  const [n, setN] = useState(10);
  useEffect(() => {
    const t = setInterval(() => setN((v) => (v <= 1 ? (k.restart(), 10) : v - 1)), 1000);
    return () => clearInterval(t);
  }, [k]);
  return (
    <div className="flex min-h-full flex-col items-center justify-center gap-6 p-8 text-center">
      <Shield className="h-24 w-24 text-success" />
      <h1 className="text-4xl font-black">Session cleared</h1>
      <p className="max-w-md text-xl text-muted-foreground">
        Your personal details have been removed from this kiosk. Thank you for using MediKiosk.
      </p>
      <p className="text-2xl font-bold">Returning to welcome in {n}s</p>
      <div className="w-full max-w-sm">
        <BigButton onClick={k.restart}>Finish now</BigButton>
      </div>
    </div>
  );
}

/* ---------- 15 Dashboard ---------- */

function Dashboard() {
  const k = useKiosk();
  const visits = [
    { d: "12 Aug 2026", dept: "Panchakarma OPD", doc: "Dr. Sharma", note: "Fever, body ache" },
    { d: "02 Jun 2026", dept: "Kayachikitsa", doc: "Dr. Iyer", note: "Acidity, poor sleep" },
    { d: "18 Jan 2026", dept: "General OPD", doc: "Dr. Bose", note: "Annual check-up" },
  ];
  return (
    <Page title="My health companion" subtitle={`ABHA ${k.patient.abha} · ${k.patient.name}`}>
      <Card className="p-5">
        <p className="text-lg font-bold">Visit timeline</p>
        <div className="mt-3 space-y-3">
          {visits.map((v) => (
            <div key={v.d} className="flex gap-3 border-l-4 border-primary pl-4">
              <div className="min-w-0">
                <p className="text-base font-bold">{v.d} · {v.dept}</p>
                <p className="text-sm text-muted-foreground">{v.doc} — {v.note}</p>
                <Button variant="outline" size="sm" className="mt-2">
                  <Download className="mr-1 h-4 w-4" /> Download summary
                </Button>
              </div>
            </div>
          ))}
        </div>
      </Card>
      <Card className="p-5">
        <p className="text-lg font-bold">Prescribed lifestyle &amp; diet (Pathya)</p>
        <ul className="mt-2 space-y-2 text-base">
          <li>🌅 Wake before 6 AM, 15 min Pranayama</li>
          <li>🍲 Warm, freshly cooked meals; avoid curd at night</li>
          <li>🚶 30 min walk after dinner</li>
          <li>🛌 Sleep by 10:30 PM, no screens in bed</li>
        </ul>
      </Card>
      <BigButton variant="outline" onClick={() => k.go("welcome")}>
        Back to kiosk view
      </BigButton>
    </Page>
  );
}

/* ---------- 16 Doctor Portal ---------- */

function DoctorPortal() {
  const k = useKiosk();
  const [confirmed, setConfirmed] = useState(false);
  const [doctorNotes, setDoctorNotes] = useState("Vitals stable. Verified patient intake and OCR lab reports.");

  const handleConfirm = async () => {
    if (k.aiSummary?.summary_id) {
      await api.doctorConfirmSummary(k.aiSummary.summary_id, doctorNotes);
    }
    setConfirmed(true);
  };

  return (
    <Page title="Doctor Consultation Portal" subtitle="Doctor's Desk · OPD Cabin 12">
      <div className="space-y-4">
        {/* Priority Triage Alert Banner if applicable */}
        {(k.complaint.toLowerCase().includes("chest pain") ||
          k.aiSummary?.red_flags_noted?.toLowerCase().includes("priority")) && (
          <Card className="border-destructive bg-destructive/15 p-4 text-destructive space-y-1">
            <div className="flex items-center gap-2 font-bold text-base">
              <AlertTriangle className="h-5 w-5" />
              PRIORITY TRIAGE ALERT — NOT A DIAGNOSIS
            </div>
            <p className="text-sm">
              Chest pain and respiratory distress noted during kiosk intake. Patient flagged for immediate bedside triage.
            </p>
          </Card>
        )}

        <Card className="p-4 space-y-3">
          <div className="flex items-center justify-between border-b pb-2">
            <div>
              <p className="font-extrabold text-lg">{k.patient.name}</p>
              <p className="text-xs text-muted-foreground">ABHA: {k.patient.abha} · {k.patient.age} y/o · {k.patient.gender}</p>
            </div>
            <div className="text-right">
              <span className="rounded-md bg-primary/10 px-2.5 py-1 text-xs font-bold text-primary">
                Token {k.tokenNumber}
              </span>
            </div>
          </div>

          <div className="grid sm:grid-cols-2 gap-3 text-sm">
            <div>
              <p className="font-semibold text-muted-foreground">Chief Complaint</p>
              <p className="font-bold">{k.complaint || "Fever and body ache"}</p>
            </div>
            <div>
              <p className="font-semibold text-muted-foreground">Severity &amp; Onset</p>
              <p className="font-bold">{k.severity}/10 · {k.answers["onset"] || "2-3 days"}</p>
            </div>
          </div>

          <div>
            <p className="font-semibold text-muted-foreground text-sm">History of Present Illness (AI Generated)</p>
            <p className="text-sm bg-muted/40 p-2.5 rounded-lg mt-1">
              {k.aiSummary?.hpi || "Patient reports fever and severe dull generalized body ache onset 3 days ago. Mild stomach pain noted after heavy meals."}
            </p>
          </div>

          {k.ocrResult && (
            <div>
              <p className="font-semibold text-muted-foreground text-sm">OCR Extracted Prescription &amp; Vitals</p>
              <div className="text-xs bg-muted/40 p-2.5 rounded-lg mt-1 space-y-1">
                <p><strong>Medicines:</strong> {k.ocrResult.entities?.medicines?.join(", ") || "Tab. Arogyavardhini Vati 250mg, Tab. Paracetamol 500mg"}</p>
                <p><strong>Extracted Vitals:</strong> Haemoglobin 9.1 g/dL, Fasting glucose 148 mg/dL</p>
              </div>
            </div>
          )}

          {k.x402Tx && (
            <div className="flex items-center justify-between rounded-lg bg-indigo-50 dark:bg-indigo-950/40 p-2.5 text-xs text-indigo-700 dark:text-indigo-300">
              <span>x402 Algorand Micropayment Settled</span>
              <a href={k.x402Tx.lora_url} target="_blank" rel="noreferrer" className="underline font-bold flex items-center gap-1">
                Lora TestNet <ExternalLink className="h-3 w-3" />
              </a>
            </div>
          )}

          <div className="space-y-1 pt-2">
            <Label className="text-sm font-semibold">Doctor&apos;s Review Notes</Label>
            <Input
              value={doctorNotes}
              onChange={(e) => setDoctorNotes(e.target.value)}
              className="text-sm"
              disabled={confirmed}
            />
          </div>
        </Card>

        <BigButton
          className={confirmed ? "bg-muted text-muted-foreground cursor-default" : "bg-success text-success-foreground"}
          onClick={handleConfirm}
          disabled={confirmed}
        >
          {confirmed ? (
            <><CheckCircle2 className="mr-2 h-6 w-6" /> Verified &amp; Confirmed by Doctor</>
          ) : (
            <><BadgeCheck className="mr-2 h-6 w-6" /> Confirm &amp; Sign Clinical Intake</>
          )}
        </BigButton>

        <BigButton variant="outline" onClick={() => k.go("welcome")}>
          Return to Kiosk View
        </BigButton>
      </div>
    </Page>
  );
}

/* ---------- router ---------- */

export function ScreenRouter() {
  const k = useKiosk();
  useEffect(() => {
    if (k.autoRead) k.speak(readoutSafe(k.screen));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [k.screen, k.autoRead]);

  switch (k.screen) {
    case "welcome":
      return <Welcome />;
    case "language":
      return <LanguageScreen />;
    case "identify":
      return <Identify />;
    case "consent":
      return <Consent />;
    case "accessibility":
      return <Accessibility />;
    case "complaint":
      return <Complaint />;
    case "socrates":
      return <Socrates />;
    case "ayush":
      return <Ayush />;
    case "emergency":
      return <Emergency />;
    case "scan":
      return <Scan />;
    case "review":
      return <Review />;
    case "summary":
      return <Summary />;
    case "token":
      return <Token />;
    case "reset":
      return <ResetScreen />;
    case "dashboard":
      return <Dashboard />;
    case "doctor":
      return <DoctorPortal />;
    default:
      return null;
  }
}
