
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useAIProviders } from '@/hooks/useAIProviders';
import { useToast } from '@/hooks/use-toast';
import { Settings, Key, Loader2, AlertCircle, CheckCircle } from 'lucide-react';

export const AIProviderSelector = () => {
  const {
    providers,
    models,
    selectedProvider,
    selectedModel,
    apiKey,
    isConnected,
    isLoading,
    setSelectedProvider,
    setSelectedModel,
    setApiKey,
    checkConnection,
  } = useAIProviders();

  const [connectionError, setConnectionError] = useState<string>('');
  const { toast } = useToast();

  const handleProviderChange = async (providerId: string) => {
    const provider = providers.find(p => p.id === providerId);
    if (provider) {
      setSelectedProvider(provider);
      setSelectedModel(null);
      setConnectionError('');
      
      try {
        const connected = await checkConnection(provider);
        if (!connected) {
          const errorMsg = provider.type === 'ollama' 
            ? 'Ollama is not running. Please start Ollama and try again.'
            : `Failed to connect to ${provider.name}. Please check your API key.`;
          setConnectionError(errorMsg);
          toast({
            title: "Connection Failed",
            description: errorMsg,
            variant: "destructive",
          });
        } else {
          toast({
            title: "Connected!",
            description: `Successfully connected to ${provider.name}`,
          });
        }
      } catch (error) {
        const errorMsg = `Error connecting to ${provider.name}: ${error instanceof Error ? error.message : 'Unknown error'}`;
        setConnectionError(errorMsg);
        toast({
          title: "Connection Error",
          description: errorMsg,
          variant: "destructive",
        });
      }
    }
  };

  const handleModelChange = (modelId: string) => {
    const model = models.find(m => m.id === modelId);
    if (model) {
      setSelectedModel(model);
      toast({
        title: "Model Selected",
        description: `Switched to ${model.name}`,
      });
    }
  };

  const handleConnect = async () => {
    if (selectedProvider) {
      setConnectionError('');
      try {
        const connected = await checkConnection(selectedProvider);
        if (!connected) {
          const errorMsg = selectedProvider.requiresApiKey && !apiKey
            ? 'API key is required for this provider'
            : 'Failed to connect. Please check your configuration.';
          setConnectionError(errorMsg);
        }
      } catch (error) {
        setConnectionError(error instanceof Error ? error.message : 'Connection failed');
      }
    }
  };

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <Settings className="w-4 h-4 text-gray-400" />
          <Label className="text-sm text-gray-400">Provider:</Label>
          <Select value={selectedProvider?.id || ''} onValueChange={handleProviderChange}>
            <SelectTrigger className="w-40 bg-gray-700 border-gray-600 hover:border-gray-500 transition-colors">
              <SelectValue placeholder="Select provider" />
            </SelectTrigger>
            <SelectContent className="bg-gray-700 border-gray-600">
              {providers.map((provider) => (
                <SelectItem key={provider.id} value={provider.id} className="hover:bg-gray-600">
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
              className="w-32 bg-gray-700 border-gray-600 text-sm focus:ring-purple-500 transition-all"
            />
          </div>
        )}

        <div className="flex items-center gap-2">
          <Label className="text-sm text-gray-400">Model:</Label>
          <Select value={selectedModel?.id || ''} onValueChange={handleModelChange} disabled={!isConnected}>
            <SelectTrigger className="w-48 bg-gray-700 border-gray-600 hover:border-gray-500 transition-colors disabled:opacity-50">
              <SelectValue placeholder={isConnected ? "Select model" : "Connect first"} />
            </SelectTrigger>
            <SelectContent className="bg-gray-700 border-gray-600">
              {models.map((model) => (
                <SelectItem key={model.id} value={model.id} className="hover:bg-gray-600">
                  {model.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {!isConnected && selectedProvider && (
          <Button 
            size="sm" 
            onClick={handleConnect} 
            variant="outline"
            disabled={isLoading}
            className="hover:bg-purple-600 hover:text-white transition-colors"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              'Connect'
            )}
          </Button>
        )}

        <div className="flex items-center gap-1">
          {isConnected ? (
            <CheckCircle className="w-4 h-4 text-green-400" />
          ) : (
            <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`} />
          )}
        </div>
      </div>

      {connectionError && (
        <Alert variant="destructive" className="max-w-md">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription className="text-sm">
            {connectionError}
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
};
