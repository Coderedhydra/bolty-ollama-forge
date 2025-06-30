
import { useState, useEffect, useCallback } from 'react';
import { AIProvider, AIModel, CodeGenerationRequest, CodeGenerationResponse } from '@/types/ai';

export const useAIProviders = () => {
  const [providers, setProviders] = useState<AIProvider[]>([
    {
      id: 'ollama',
      name: 'Ollama (Local)',
      type: 'ollama',
      baseUrl: 'http://localhost:11434',
      requiresApiKey: false,
    },
    {
      id: 'openai',
      name: 'OpenAI GPT',
      type: 'openai',
      baseUrl: 'https://api.openai.com/v1',
      requiresApiKey: true,
    },
    {
      id: 'anthropic',
      name: 'Anthropic Claude',
      type: 'anthropic',
      baseUrl: 'https://api.anthropic.com/v1',
      requiresApiKey: true,
    },
  ]);

  const [models, setModels] = useState<AIModel[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<AIProvider | null>(null);
  const [selectedModel, setSelectedModel] = useState<AIModel | null>(null);
  const [apiKey, setApiKey] = useState<string>('');
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Update connection state when provider or model changes
  useEffect(() => {
    if (selectedProvider && selectedModel) {
      setIsConnected(true);
    } else {
      setIsConnected(false);
    }
  }, [selectedProvider, selectedModel]);

  const checkConnection = useCallback(async (provider: AIProvider) => {
    setIsLoading(true);
    try {
      switch (provider.type) {
        case 'ollama':
          const ollamaResponse = await fetch(`${provider.baseUrl}/api/tags`);
          if (ollamaResponse.ok) {
            const data = await ollamaResponse.json();
            const ollamaModels = data.models.map((model: any) => ({
              id: model.name,
              name: model.name,
              provider: provider.id,
              contextLength: 4096,
              supportsCodeGeneration: true,
            }));
            setModels(ollamaModels);
            // Auto-select the first model if available
            if (ollamaModels.length > 0) {
              setSelectedModel(ollamaModels[0]);
            }
            return true;
          }
          break;
        
        case 'openai':
          if (!apiKey) {
            setIsConnected(false);
            return false;
          }
          const openaiResponse = await fetch(`${provider.baseUrl}/models`, {
            headers: { Authorization: `Bearer ${apiKey}` },
          });
          if (openaiResponse.ok) {
            const data = await openaiResponse.json();
            const openaiModels = data.data
              .filter((model: any) => model.id.includes('gpt'))
              .map((model: any) => ({
                id: model.id,
                name: model.id,
                provider: provider.id,
                contextLength: model.id.includes('gpt-4') ? 8192 : 4096,
                supportsCodeGeneration: true,
              }));
            setModels(openaiModels);
            // Auto-select GPT-4 if available, otherwise first model
            const preferredModel = openaiModels.find((m: any) => m.id.includes('gpt-4')) || openaiModels[0];
            if (preferredModel) {
              setSelectedModel(preferredModel);
            }
            return true;
          }
          break;

        case 'anthropic':
          if (!apiKey) {
            setIsConnected(false);
            return false;
          }
          // For Anthropic, we'll set predefined models since they don't have a models endpoint
          const anthropicModels = [
            {
              id: 'claude-3-5-sonnet-20241022',
              name: 'Claude 3.5 Sonnet',
              provider: provider.id,
              contextLength: 200000,
              supportsCodeGeneration: true,
            },
            {
              id: 'claude-3-haiku-20240307',
              name: 'Claude 3 Haiku',
              provider: provider.id,
              contextLength: 200000,
              supportsCodeGeneration: true,
            },
          ];
          setModels(anthropicModels);
          // Auto-select the first model
          setSelectedModel(anthropicModels[0]);
          return true;
      }
    } catch (error) {
      console.error(`Failed to connect to ${provider.name}:`, error);
      setIsConnected(false);
      setModels([]);
      setSelectedModel(null);
      return false;
    } finally {
      setIsLoading(false);
    }
    
    setIsConnected(false);
    setModels([]);
    setSelectedModel(null);
    return false;
  }, [apiKey]);

  // Custom setter for selectedProvider that also triggers connection check
  const handleSetSelectedProvider = useCallback(async (provider: AIProvider | null) => {
    setSelectedProvider(provider);
    setSelectedModel(null);
    setModels([]);
    setIsConnected(false);
    
    if (provider) {
      await checkConnection(provider);
    }
  }, [checkConnection]);

  // Custom setter for selectedModel that updates connection state
  const handleSetSelectedModel = useCallback((model: AIModel | null) => {
    setSelectedModel(model);
    if (model && selectedProvider) {
      setIsConnected(true);
    }
  }, [selectedProvider]);

  const generateCode = useCallback(async (request: CodeGenerationRequest): Promise<CodeGenerationResponse> => {
    if (!selectedProvider || !selectedModel || !isConnected) {
      throw new Error('No provider/model selected or not connected');
    }

    setIsLoading(true);

    try {
      const systemPrompt = `You are an expert web developer and coding assistant. Generate clean, modern, and functional web code based on user requests.

IMPORTANT INSTRUCTIONS:
1. Always return valid JSON in this exact format:
{
  "files": [
    {
      "fileName": "example.html",
      "content": "file content here",
      "language": "html"
    }
  ],
  "explanation": "Brief explanation of what was created",
  "suggestions": ["suggestion 1", "suggestion 2"]
}

2. Create complete, working files with proper structure
3. Use modern web technologies (HTML5, CSS3, ES6+)
4. Include responsive design
5. Add proper error handling where needed
6. Generate multiple files if needed (HTML, CSS, JS)
7. Make sure all code is production-ready

Current project context:
${Object.entries(request.context).map(([name, content]) => `${name}:\n${content.substring(0, 1000)}...`).join('\n\n')}

Request type: ${request.type}
${request.errorMessage ? `Error to fix: ${request.errorMessage}` : ''}
${request.currentFile ? `Current file: ${request.currentFile}` : ''}`;

      let response;

      switch (selectedProvider.type) {
        case 'ollama':
          response = await fetch(`${selectedProvider.baseUrl}/api/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              model: selectedModel.id,
              prompt: `${systemPrompt}\n\nUser request: ${request.prompt}`,
              stream: false,
            }),
          });
          break;

        case 'openai':
          response = await fetch(`${selectedProvider.baseUrl}/chat/completions`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${apiKey}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              model: selectedModel.id,
              messages: [
                { role: 'system', content: systemPrompt },
                { role: 'user', content: request.prompt },
              ],
              temperature: 0.7,
            }),
          });
          break;

        case 'anthropic':
          response = await fetch(`${selectedProvider.baseUrl}/messages`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${apiKey}`,
              'Content-Type': 'application/json',
              'anthropic-version': '2023-06-01',
            },
            body: JSON.stringify({
              model: selectedModel.id,
              max_tokens: 4000,
              messages: [
                { role: 'user', content: `${systemPrompt}\n\nUser request: ${request.prompt}` },
              ],
            }),
          });
          break;

        default:
          throw new Error('Unsupported provider');
      }

      if (!response?.ok) {
        throw new Error(`API request failed: ${response?.status}`);
      }

      const data = await response.json();
      let content = '';

      switch (selectedProvider.type) {
        case 'ollama':
          content = data.response;
          break;
        case 'openai':
          content = data.choices[0].message.content;
          break;
        case 'anthropic':
          content = data.content[0].text;
          break;
      }

      // Try to parse JSON response
      try {
        const jsonMatch = content.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          return JSON.parse(jsonMatch[0]);
        }
      } catch (e) {
        // If JSON parsing fails, create a simple response
        return {
          files: [
            {
              fileName: 'index.html',
              content: content,
              language: 'html',
            },
          ],
          explanation: 'Generated code based on your request',
          suggestions: ['Review the generated code', 'Test in browser', 'Customize as needed'],
        };
      }

      throw new Error('Invalid response format');
    } catch (error) {
      console.error('Error generating code:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [selectedProvider, selectedModel, apiKey, isConnected]);

  return {
    providers,
    models,
    selectedProvider,
    selectedModel,
    apiKey,
    isConnected,
    isLoading,
    setSelectedProvider: handleSetSelectedProvider,
    setSelectedModel: handleSetSelectedModel,
    setApiKey,
    checkConnection,
    generateCode,
  };
};
