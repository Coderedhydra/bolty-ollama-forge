
import { useState, useEffect, useCallback } from 'react';

interface OllamaModel {
  name: string;
  modified_at: string;
  size: number;
}

export const useOllama = () => {
  const [models, setModels] = useState<string[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const checkConnection = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:11434/api/tags');
      if (response.ok) {
        setIsConnected(true);
        const data = await response.json();
        const modelNames = data.models.map((model: OllamaModel) => model.name);
        setModels(modelNames);
        
        if (modelNames.length > 0 && !selectedModel) {
          setSelectedModel(modelNames[0]);
        }
      } else {
        setIsConnected(false);
      }
    } catch (error) {
      console.error('Failed to connect to Ollama:', error);
      setIsConnected(false);
    }
  }, [selectedModel]);

  const generateCode = useCallback(async (prompt: string, context: Record<string, string>) => {
    if (!selectedModel || !isConnected) {
      throw new Error('No model selected or Ollama not connected');
    }

    setIsLoading(true);
    
    try {
      const systemPrompt = `You are an expert web developer. Generate clean, modern, and functional web code based on user requests. 
      Consider the existing project context and create cohesive solutions. 
      Return only the code without explanations unless specifically asked.
      
      Current project files:
      ${Object.entries(context).map(([name, content]) => `${name}:\n${content}`).join('\n\n')}`;

      const response = await fetch('http://localhost:11434/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: selectedModel,
          prompt: `${systemPrompt}\n\nUser request: ${prompt}`,
          stream: false,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate code');
      }

      const data = await response.json();
      return data.response;
    } catch (error) {
      console.error('Error generating code:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [selectedModel, isConnected]);

  const fixBugs = useCallback(async (code: string, errorMessage?: string) => {
    if (!selectedModel || !isConnected) {
      throw new Error('No model selected or Ollama not connected');
    }

    const prompt = `Fix the bugs in this code${errorMessage ? ` (Error: ${errorMessage})` : ''}:\n\n${code}`;
    return generateCode(prompt, {});
  }, [selectedModel, isConnected, generateCode]);

  useEffect(() => {
    checkConnection();
    const interval = setInterval(checkConnection, 5000);
    return () => clearInterval(interval);
  }, [checkConnection]);

  return {
    models,
    selectedModel,
    setSelectedModel,
    isConnected,
    isLoading,
    generateCode,
    fixBugs,
    checkConnection,
  };
};
