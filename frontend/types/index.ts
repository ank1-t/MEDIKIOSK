export type SupportedLanguage = 'en' | 'hi';

export interface QuestionOption {
  id: string;
  label_en: string;
  label_hi: string;
}

export interface Question {
  id: string;
  type: 'yes_no' | 'single_choice' | 'multi_choice' | 'number' | 'date' | 'text';
  text_en: string;
  text_hi: string;
  audio_en?: string;
  audio_hi?: string;
  options?: QuestionOption[];
  mandatory?: boolean;
}

export interface PatientSession {
  sessionId: string;
  demoId: string;
  language: SupportedLanguage;
  step: number;
}

export interface ClinicalSummary {
  chief_complaint: string;
  history_of_present_illness: string;
  past_medical_history: string[];
  medications: string[];
  allergies: string[];
  alerts: string[];
}
