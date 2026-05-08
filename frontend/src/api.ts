import axios, { AxiosError } from "axios";
import type { AnalysisRequest, AnalysisResponse, HistoryItem } from "./types";

const api = axios.create({
  baseURL: "http://localhost:8000",
  timeout: 30000,
});

export const mapAnalysisRequestToApiPayload = (request: AnalysisRequest) => ({
  text: request.text,
  context: request.context ?? null,
  language_override: request.languageOverride ?? null,
});

const friendlyError = (error: unknown): Error => {
  if (axios.isAxiosError(error)) {
    const err = error as AxiosError<{ detail?: string; error?: string }>;
    if (!err.response) {
      return new Error("Backend is not running. Please start the server.");
    }
    return new Error(err.response.data?.detail || err.response.data?.error || "Request failed");
  }
  return new Error("Unexpected error occurred");
};

export const analyzeText = async (request: AnalysisRequest): Promise<AnalysisResponse> => {
  try {
    const response = await api.post<AnalysisResponse>("/analyze", mapAnalysisRequestToApiPayload(request));
    return response.data;
  } catch (error) {
    throw friendlyError(error);
  }
};

export const analyzeFile = async (file: File, request: Omit<AnalysisRequest, "text">): Promise<AnalysisResponse> => {
  const formData = new FormData();
  formData.append("file", file);
  if (request.context) {
    formData.append("context", request.context);
  }
  if (request.languageOverride) {
    formData.append("language_override", request.languageOverride);
  }

  try {
    const response = await api.post<AnalysisResponse>("/analyze-file", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  } catch (error) {
    throw friendlyError(error);
  }
};

export const getHistory = async (): Promise<HistoryItem[]> => {
  try {
    const response = await api.get<HistoryItem[]>("/history");
    return response.data;
  } catch (error) {
    throw friendlyError(error);
  }
};

export const getThreshold = async (): Promise<number> => {
  try {
    const response = await api.get<{ threshold: number }>("/threshold");
    return response.data.threshold;
  } catch (error) {
    throw friendlyError(error);
  }
};

export const setThreshold = async (threshold: number): Promise<number> => {
  try {
    const response = await api.post<{ threshold: number }>("/threshold", { threshold });
    return response.data.threshold;
  } catch (error) {
    throw friendlyError(error);
  }
};
