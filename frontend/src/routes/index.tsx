import { createFileRoute } from "@tanstack/react-router";
import { KioskProvider } from "@/kiosk/context";
import { DemoBar, KioskShell } from "@/kiosk/shell";
import { ScreenRouter } from "@/kiosk/screens";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "MediKiosk — AYUSH Hospital OPD Self Check-In Kiosk" },
      {
        name: "description",
        content:
          "MediKiosk is a multilingual touchscreen OPD check-in kiosk for Indian AYUSH hospitals: ABHA identification, DPDP consent, voice symptom intake and instant token printing.",
      },
      { property: "og:title", content: "MediKiosk — AYUSH Hospital OPD Self Check-In Kiosk" },
      {
        property: "og:description",
        content:
          "Touchscreen kiosk flow for AIIA OPD: language selection, ABHA login, voice-led symptom interview, Dashavidha Pariksha and token generation.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Index,
});

function Index() {
  return (
    <KioskProvider>
      <div className="min-h-screen bg-muted/40">
        <DemoBar />
        <KioskShell>
          <ScreenRouter />
        </KioskShell>
      </div>
    </KioskProvider>
  );
}
