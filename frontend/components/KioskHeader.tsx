import React from 'react';

interface KioskHeaderProps {
  currentStep?: number;
  totalSteps?: number;
  onReset?: () => void;
}

export const KioskHeader: React.FC<KioskHeaderProps> = ({
  currentStep = 1,
  totalSteps = 5,
  onReset,
}) => {
  return (
    <header className="kiosk-header">
      <div className="logo-container">
        <div className="logo-badge">➕</div>
        <div>
          <h1 className="logo-title">MediKiosk</h1>
          <p className="logo-subtitle">Clinical Intake Assistant • क्लिनिकल इंटेक सहायक</p>
        </div>
      </div>
      <div className="progress-container">
        <span className="step-badge">Step {currentStep} / {totalSteps}</span>
        {onReset && (
          <button onClick={onReset} className="reset-btn">
            Restart / पुनः प्रारंभ
          </button>
        )}
      </div>
    </header>
  );
};
