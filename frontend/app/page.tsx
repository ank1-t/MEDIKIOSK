'use client';

import React, { useState } from 'react';
import { KioskHeader } from '../components/KioskHeader';

export default function HomePage() {
  const [selectedLanguage, setSelectedLanguage] = useState<'en' | 'hi'>('en');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <KioskHeader currentStep={1} totalSteps={5} />

      <main className="main-container" style={{ textAlign: 'center' }}>
        <h2 style={{ fontSize: '2rem', marginBottom: '0.75rem', color: 'var(--text-main)' }}>
          {selectedLanguage === 'en' ? 'Welcome to MediKiosk' : 'मेडीकिओस्क में आपका स्वागत है'}
        </h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: '2.5rem', fontSize: '1.15rem' }}>
          {selectedLanguage === 'en'
            ? 'Fast, accessible pre-consultation intake. Answer by voice or touch.'
            : 'त्वरित और आसान प्री-परामर्श इंटेक। आवाज या स्पर्श द्वारा उत्तर दें।'}
        </p>

        {/* Language Selection Buttons */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '1.5rem', marginBottom: '3rem' }}>
          <button
            type="button"
            onClick={() => setSelectedLanguage('en')}
            style={{
              padding: '1rem 2rem',
              fontSize: '1.25rem',
              borderRadius: 'var(--radius-md)',
              border: selectedLanguage === 'en' ? '2px solid var(--primary)' : '1px solid var(--border)',
              background: selectedLanguage === 'en' ? '#e0f2fe' : 'white',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            English
          </button>
          <button
            type="button"
            onClick={() => setSelectedLanguage('hi')}
            style={{
              padding: '1rem 2rem',
              fontSize: '1.25rem',
              borderRadius: 'var(--radius-md)',
              border: selectedLanguage === 'hi' ? '2px solid var(--primary)' : '1px solid var(--border)',
              background: selectedLanguage === 'hi' ? '#e0f2fe' : 'white',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            हिंदी (Hindi)
          </button>
        </div>

        <div>
          <button type="button" className="btn-large">
            {selectedLanguage === 'en' ? 'Start Intake / शुरू करें →' : 'इंटेक शुरू करें →'}
          </button>
        </div>
      </main>
    </div>
  );
}
