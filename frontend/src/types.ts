export enum Language {
  AUTO = "auto",
  ARABIC = "arabic",
  DARIJA = "darija",
  FRENCH = "french",
  ENGLISH = "english",
  UNKNOWN = "unknown",
}

export interface AnalysisRequest {
  text: string;
  context?: string | null;
  languageOverride?: Exclude<Language, Language.AUTO> | null;
}

export type SarcasmType =
  | "polarity_contrast"
  | "exaggeration"
  | "rhetorical_question"
  | "ironic_comparison"
  | "none";

export type TargetType =
  | "person"
  | "organization"
  | "product"
  | "situation"
  | "government"
  | "none";

export interface AnalysisResponse {
  is_sarcastic: boolean;
  confidence: number;
  language: Exclude<Language, Language.AUTO>;
  sarcasm_type: SarcasmType;
  target: TargetType;
  intensity: 1 | 2 | 3 | 4 | 5;
  explanation: string;
  indicators: string[];
  threshold: number;
  extracted_text?: string;
}

export interface HistoryItem extends AnalysisResponse {
  text: string;
  timestamp: string;
}
