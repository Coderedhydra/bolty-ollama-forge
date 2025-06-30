
import React from 'react';
import { Header } from '@/components/Header';
import { Sidebar } from '@/components/Sidebar';
import { CodeEditor } from '@/components/CodeEditor';
import { Preview } from '@/components/Preview';
import { ChatPanel } from '@/components/ChatPanel';
import { useAIProviders } from '@/hooks/useAIProviders';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { AlertCircle, RefreshCw, ExternalLink } from 'lucide-react';

const Index = () => {
  const { isConnected, selectedProvider, checkConnection } = useAIProviders();

  const handleRetryConnection = async () => {
    if (selectedProvider) {
      await checkConnection(selectedProvider);
    }
  };

  const ConnectionPrompt = () => (
    <div className="absolute inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-gray-800 p-8 rounded-lg border border-gray-700 max-w-lg mx-4">
        <div className="flex items-center gap-3 mb-4">
          <AlertCircle className="w-6 h-6 text-amber-400" />
          <h3 className="text-lg font-semibold">AI Provider Required</h3>
        </div>
        
        {selectedProvider ? (
          <div className="space-y-4">
            <p className="text-gray-400">
              Failed to connect to <span className="font-medium text-white">{selectedProvider.name}</span>
            </p>
            
            {selectedProvider.type === 'ollama' && (
              <Alert className="bg-blue-900/20 border-blue-700">
                <AlertTitle className="text-blue-400">Ollama Setup Required</AlertTitle>
                <AlertDescription className="text-gray-300">
                  <div className="mt-2 space-y-2">
                    <p>1. Install Ollama from <a href="https://ollama.ai" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline inline-flex items-center gap-1">ollama.ai <ExternalLink className="w-3 h-3" /></a></p>
                    <p>2. Run: <code className="bg-gray-700 px-2 py-1 rounded text-sm">ollama serve</code></p>
                    <p>3. Pull a model: <code className="bg-gray-700 px-2 py-1 rounded text-sm">ollama pull llama2</code></p>
                  </div>
                </AlertDescription>
              </Alert>
            )}
            
            {selectedProvider.requiresApiKey && (
              <Alert className="bg-amber-900/20 border-amber-700">
                <AlertTitle className="text-amber-400">API Key Required</AlertTitle>
                <AlertDescription className="text-gray-300">
                  Please enter your {selectedProvider.name} API key in the header to continue.
                </AlertDescription>
              </Alert>
            )}
            
            <Button onClick={handleRetryConnection} className="w-full" variant="outline">
              <RefreshCw className="w-4 h-4 mr-2" />
              Retry Connection
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            <p className="text-gray-400">
              Please select an AI provider from the header to start generating code.
            </p>
            
            <Alert className="bg-gray-900/50 border-gray-600">
              <AlertTitle>Available Providers</AlertTitle>
              <AlertDescription className="text-gray-300">
                <div className="mt-2 space-y-1">
                  <p>• <strong>Ollama</strong> - Run AI models locally (free)</p>
                  <p>• <strong>OpenAI</strong> - GPT models (requires API key)</p>
                  <p>• <strong>Anthropic</strong> - Claude models (requires API key)</p>
                </div>
              </AlertDescription>
            </Alert>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="h-screen bg-gray-900 text-white flex flex-col overflow-hidden">
      <Header />
      
      <div className="flex-1 flex overflow-hidden relative">
        <Sidebar />
        
        <div className="flex-1 flex">
          <div className="flex-1 flex flex-col">
            <CodeEditor />
          </div>
          
          <div className="w-1/2 flex flex-col border-l border-gray-700">
            <Preview />
          </div>
        </div>
        
        <ChatPanel />
        
        {!isConnected && <ConnectionPrompt />}
      </div>
    </div>
  );
};

export default Index;
