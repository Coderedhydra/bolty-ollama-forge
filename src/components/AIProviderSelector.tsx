
import React from 'react';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useAIProviders } from '@/hooks/useAIProviders';
import { Settings, Key } from 'lucide-react';

export const AIProviderSelector = () => {
  const {
    providers,
    models,
    selectedProvider,
    selectedModel,
    apiKey,
    isConnected,
    setSelectedProvider,
    setSelectedModel,
    setApiKey,
    checkConnection,
  } = useAIProviders();

  const handleProviderChange = (providerId: string) => {
    const provider = providers.find(p => p.id === providerId);
    if (provider) {
      setSelectedProvider(provider);
      setSelectedModel(null);
      checkConnection(provider);
    }
  };

  const handleModelChange = (modelId: string) => {
    const model = models.find(m => m.id === modelId);
    if (model) {
      setSelectedModel(model);
    }
  };

  const handleConnect = () => {
    if (selectedProvider) {
      checkConnection(selectedProvider);
    }
  };

  return (
    <div className="flex items-center gap-4">
      <div className="flex items-center gap-2">
        <Settings className="w-4 h-4 text-gray-400" />
        <Label className="text-sm text-gray-400">Provider:</Label>
        <Select value={selectedProvider?.id || ''} onValueChange={handleProviderChange}>
          <SelectTrigger className="w-40 bg-gray-700 border-gray-600">
            <SelectValue placeholder="Select provider" />
          </SelectTrigger>
          <SelectContent>
            {providers.map((provider) => (
              <SelectItem key={provider.id} value={provider.id}>
                {provider.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {selectedProvider?.requiresApiKey && (
        <div className="flex items-center gap-2">
          <Key className="w-4 h-4 text-gray-400" />
          <Input
            type="password"
            placeholder="API Key"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            className="w-32 bg-gray-700 border-gray-600 text-sm"
          />
        </div>
      )}

      <div className="flex items-center gap-2">
        <Label className="text-sm text-gray-400">Model:</Label>
        <Select value={selectedModel?.id || ''} onValueChange={handleModelChange}>
          <SelectTrigger className="w-48 bg-gray-700 border-gray-600">
            <SelectValue placeholder="Select model" />
          </SelectTrigger>
          <SelectContent>
            {models.map((model) => (
              <SelectItem key={model.id} value={model.id}>
                {model.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {!isConnected && selectedProvider && (
        <Button size="sm" onClick={handleConnect} variant="outline">
          Connect
        </Button>
      )}

      <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`} />
    </div>
  );
};
