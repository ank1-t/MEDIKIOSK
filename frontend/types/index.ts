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

export interface DocumentRecord {
  id: number;
  session_id: string;
  filename: string;
  file_path?: string;
  type: string;
  uploaded_at: string;
  text?: string;
  extracted_data?: {
    raw_text?: string;
    source?: string;
    document_date?: string;
    medicines?: string[];
    hospital_name?: string;
    entities?: {
      dates?: string[];
      primary_date?: string;
      medicines?: Array<{ name: string; raw_match: string; type: string }>;
      clinic_name?: string;
      doctor_name?: string;
    };
  };
}

export interface TimelineItem {
  id: string;
  item_type: 'document' | 'answer';
  title: string;
  date_or_time: string;
  timestamp: string;
  details: {
    document_id?: number;
    filename?: string;
    file_path?: string;
    type?: string;
    text?: string;
    medicines?: string[];
    clinic_name?: string;
    doctor_name?: string;
    question_id?: string;
    answer_text?: string;
    source?: string;
  };
}
