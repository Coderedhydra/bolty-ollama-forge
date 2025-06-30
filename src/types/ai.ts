
export interface AIProvider {
  id: string;
  name: string;
  type: 'ollama' | 'openai' | 'anthropic' | 'custom';
  baseUrl?: string;
  requiresApiKey: boolean;
}

export interface AIModel {
  id: string;
  name: string;
  provider: string;
  contextLength: number;
  supportsCodeGeneration: boolean;
}

export interface CodeGenerationRequest {
  prompt: string;
  context: Record<string, string>;
  currentFile?: string;
  errorMessage?: string;
  type: 'generate' | 'fix' | 'enhance' | 'refactor';
}

export interface GeneratedFile {
  fileName: string;
  content: string;
  language: string;
}

export interface CodeGenerationResponse {
  files: GeneratedFile[];
  explanation: string;
  suggestions: string[];
}
