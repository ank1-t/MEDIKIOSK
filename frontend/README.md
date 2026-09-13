# MediKiosk Assist

Build "MediKiosk" — a comprehensive touchscreen hospital kiosk UI designed for Indian hospital OPDs (AIIA / Ministry of AYUSH, SIH 2026 Problem Statement 4) with portrait kiosk simulation mode and full flow:

1. Global Design & Kiosk Shell:
- High-contrast, warm clinical theme (deep teal/slate blue, mint/emerald success accents, soft clean background).
- Portrait kiosk aspect ratio toggle (view as kiosk portrait frame 9:16 / 21"-24" touchscreen with bezel, or responsive fullscreen).
- Persistent header/footer: Back, Home/Restart, Help/Call Staff (with instant modal), Language pill, live date/time, and emergency helpline.
- Global audio icon (🔊) with web SpeechSynthesis audio playback of instructions on every screen.
- Inactivity countdown timer with a "Still there?" modal and auto-reset to Welcome screen.
- Global progress indicator for the interview steps. Large touch targets (min 64px), readable typography (32px+ headings, 20px+ body).

2. Page-by-Page Kiosk Flow:
- Page 1: Idle / Welcome Attract-Loop screen with hospital branding (AIIA / Ministry of AYUSH badges), animated pulse, rotating multilingual "Touch to Start / शुरू करने के लिए छुएं", live OPD token counter.
- Page 2: Language Selection grid (Hindi, English, Marathi, Tamil, Bengali, Telugu, Gujarati) with native script tiles, audio preview greeting on first tap, highlight-confirm transition.
- Page 3: Patient Identification: 3 large cards ("Scan ABHA QR" with simulated camera overlay, "Enter ABHA / Aadhaar" with custom big numeric keypad, "New Patient / Register" with minimal 4-field touch form: Name, Age, Gender, Mobile).
- Page 4: DPDP Act Consent: Granular toggles for Voice Recording, Document Scanning, and Sharing with Doctor/ABHA, audio read-out button, master Agree vs Decline (redirect to staff desk).
- Page 5: Accessibility Setup (skippable): Toggles for High Contrast / Large Text, Audio-Guided Auto-Read mode, and Sign Language avatar assistant preview.
- Page 6: Chief Complaint (Interview Step 1): Large pulsing mic with simulated real-time voice speech recognition transcription + grid of common quick-tap symptom cards (Fever, Abdominal Pain, Cough/Breathing, Joint/Body Ache, Skin Issue, Other).
- Page 7: Adaptive SOCRATES Follow-up: Interactive probing (Onset, Severity slider, Pain body-map selector front/back, Nature of pain chips, Aggravating factors). Includes "I don't know / Skip" button.
- Page 8: AYUSH History Mode (toggleable / conditioned on AYUSH OPD): Dashavidha Pariksha evaluation (Prakriti, Agni/digestion, Nidra/sleep, Ahara/diet, Bala, Satva) with simple patient-friendly Hindi/English explanations and icons.
- Page 9: Red-Flag / Emergency Interrupt State: Demo trigger button + alert screen (urgent amber/red, "Hospital Staff Alerted - Nurse en route", Emergency Token #, flashing beacon, reassuring tone).
- Page 10: Document Upload / Camera Scanner: Simulated webcam/scanner viewfinder with alignment guide, capture flash, document detection, multi-page filmstrip, and OCR parsing animation.
- Page 11: Document Review: Split preview of scanned slip and OCR-extracted fields (medication names, dates, lab values with out-of-range visual highlights) with quick checkmark approval.
- Page 12: Structured Summary Preview: Patient-friendly recap card (Chief Complaint, History timeline, Scanned files), text-to-speech summary, "Confirm" vs "Edit" jump links.
- Page 13: Submission & Token Screen: Big animated green tick, large OPD Token Number (e.g., OPD-AYUSH-104), estimated wait time, assigned Doctor/Cabin (e.g. Dr. Sharma, Room 12), and interactive "Print Token" receipt preview.
- Page 14: Privacy Confirmation & Session Reset: "Session Cleared" countdown returning to Welcome.
- Page 15: Separate Patient Dashboard View: Switchable view showing the home/mobile companion web app (ABHA login, timeline of past OPD visits, downloadable summaries, prescribed lifestyle/diet chart).

Include a top demo navigation bar to easily jump between any of the 15 screens, test the emergency trigger, and toggle AYUSH mode or Kiosk/Desktop frame view.

This project was built with [Lovable](https://lovable.dev).

## Build with Lovable

Continue developing this project in the [Lovable editor](https://lovable.dev/projects/b09ef29d-ece1-42c0-ab84-fd2839af38d0).

- **Ship faster**: describe what you want to build and Lovable handles the code.
- **Stay in sync**: every change made in Lovable is committed straight to this repository.
- **Full ownership**: this code is yours. Push to `main` on GitHub and your changes sync back into Lovable, ready for your next prompt.

## Development

Prefer working locally? You need Node.js and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating).

```sh
git clone <this-repository-url>
cd <repository-name>
npm i
npm run dev
```
