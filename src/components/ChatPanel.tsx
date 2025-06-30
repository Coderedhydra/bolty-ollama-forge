
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useAIProviders } from '@/hooks/useAIProviders';
import { useProjectStore } from '@/stores/projectStore';
import { useToast } from '@/hooks/use-toast';
import { Send, MessageSquare, Code, Bug, Sparkles, FileText, AlertCircle, Loader2 } from 'lucide-react';

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant' | 'error';
  content: string;
  timestamp: Date;
}

export const ChatPanel = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { generateCode, isConnected, selectedProvider, selectedModel } = useAIProviders();
  const { files, addFile, updateFile, currentFile, generatePreview } = useProjectStore();
  const { toast } = useToast();

  const addMessage = (message: Omit<ChatMessage, 'id' | 'timestamp'>) => {
    const newMessage: ChatMessage = {
      ...message,
      id: Date.now().toString(),
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, newMessage]);
    return newMessage;
  };

  const handleSend = async () => {
    if (!input.trim()) return;
    
    if (!isConnected) {
      addMessage({
        type: 'error',
        content: 'Please connect to an AI provider first.',
      });
      return;
    }

    if (!selectedModel) {
      addMessage({
        type: 'error',
        content: 'Please select a model first.',
      });
      return;
    }

    const userMessage = addMessage({
      type: 'user',
      content: input,
    });

    setInput('');
    setIsLoading(true);

    try {
      const response = await generateCode({
        prompt: input,
        context: files,
        currentFile: currentFile || undefined,
        type: 'generate',
      });

      // Add generated files to project
      let filesAdded = 0;
      response.files.forEach(file => {
        addFile(file.fileName, file.content);
        filesAdded++;
      });

      // Generate preview after adding files
      if (filesAdded > 0) {
        generatePreview();
      }

      addMessage({
        type: 'assistant',
        content: `${response.explanation}\n\n📁 Generated ${filesAdded} file(s):\n${response.files.map(f => `• ${f.fileName}`).join('\n')}\n\n💡 Suggestions:\n${response.suggestions.map(s => `• ${s}`).join('\n')}`,
      });

      toast({
        title: "Code Generated!",
        description: `Created ${filesAdded} file(s) successfully`,
      });

    } catch (error) {
      console.error('Error generating code:', error);
      
      let errorMessage = 'Failed to generate code';
      if (error instanceof Error) {
        if (error.message.includes('NetworkError')) {
          errorMessage = selectedProvider?.type === 'ollama' 
            ? 'Cannot connect to Ollama. Please make sure Ollama is running on localhost:11434'
            : 'Network error - please check your internet connection';
        } else if (error.message.includes('401')) {
          errorMessage = 'Invalid API key - please check your credentials';
        } else if (error.message.includes('429')) {
          errorMessage = 'Rate limit exceeded - please wait a moment and try again';
        } else {
          errorMessage = error.message;
        }
      }

      addMessage({
        type: 'error',
        content: errorMessage,
      });

      toast({
        title: "Generation Failed",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickAction = (action: string) => {
    setInput(action);
  };

  const handleFixBugs = async () => {
    if (!currentFile || !isConnected) {
      toast({
        title: "Cannot Fix Bugs",
        description: !currentFile ? "Please select a file first" : "Please connect to an AI provider",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    try {
      const response = await generateCode({
        prompt: 'Fix any bugs or issues in this code',
        context: files,
        currentFile,
        type: 'fix',
      });

      if (response.files.length > 0) {
        const fixedFile = response.files[0];
        updateFile(fixedFile.fileName, fixedFile.content);
        generatePreview();

        addMessage({
          type: 'assistant',
          content: `🔧 Fixed bugs in ${fixedFile.fileName}:\n${response.explanation}`,
        });

        toast({
          title: "Bugs Fixed!",
          description: `Updated ${fixedFile.fileName}`,
        });
      }
    } catch (error) {
      console.error('Error fixing bugs:', error);
      addMessage({
        type: 'error',
        content: `Failed to fix bugs: ${error instanceof Error ? error.message : 'Unknown error'}`,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-80 bg-gray-800 border-l border-gray-700 flex flex-col">
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center gap-2 mb-4">
          <MessageSquare className="w-5 h-5 text-purple-400" />
          <h2 className="text-sm font-semibold text-gray-300">AI Assistant</h2>
          {selectedModel && (
            <span className="text-xs bg-purple-600/20 text-purple-300 px-2 py-1 rounded">
              {selectedModel.name}
            </span>
          )}
        </div>
        
        <div className="grid grid-cols-2 gap-2 mb-4">
          <Button
            size="sm"
            variant="outline"
            onClick={() => handleQuickAction('Create a modern landing page with hero section')}
            disabled={!isConnected}
            className="hover:bg-purple-600/20 transition-colors"
          >
            <Code className="w-3 h-3 mr-1" />
            Generate
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={handleFixBugs}
            disabled={!currentFile || isLoading || !isConnected}
            className="hover:bg-red-600/20 transition-colors"
          >
            <Bug className="w-3 h-3 mr-1" />
            Fix Bugs
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => handleQuickAction('Create a React component with modern styling')}
            disabled={!isConnected}
            className="hover:bg-blue-600/20 transition-colors"
          >
            <Sparkles className="w-3 h-3 mr-1" />
            Component
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => handleQuickAction('Make this design fully responsive')}
            disabled={!isConnected}
            className="hover:bg-green-600/20 transition-colors"
          >
            <FileText className="w-3 h-3 mr-1" />
            Responsive
          </Button>
        </div>

        {!isConnected && (
          <Alert variant="destructive" className="text-xs">
            <AlertCircle className="w-4 h-4" />
            <AlertDescription>
              {selectedProvider 
                ? `Not connected to ${selectedProvider.name}` 
                : 'Please select and connect to an AI provider'
              }
            </AlertDescription>
          </Alert>
        )}
      </div>

      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-500 py-8">
              <MessageSquare className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p className="text-sm">Start a conversation with AI</p>
              <p className="text-xs mt-1">Use the quick actions or type your request</p>
            </div>
          )}
          
          {messages.map((message) => (
            <div
              key={message.id}
              className={`p-3 rounded-lg transition-all duration-200 ${
                message.type === 'user'
                  ? 'bg-purple-600 ml-4 shadow-lg'
                  : message.type === 'error'
                  ? 'bg-red-900/50 border border-red-700 mr-4'
                  : 'bg-gray-700 mr-4 shadow-md'
              }`}
            >
              {message.type === 'error' && (
                <div className="flex items-center gap-2 mb-2">
                  <AlertCircle className="w-4 h-4 text-red-400" />
                  <span className="text-sm font-medium text-red-400">Error</span>
                </div>
              )}
              <p className="text-sm text-white whitespace-pre-wrap leading-relaxed">
                {message.content}
              </p>
              <span className="text-xs text-gray-400 mt-2 block">
                {message.timestamp.toLocaleTimeString()}
              </span>
            </div>
          ))}
          
          {isLoading && (
            <div className="bg-gray-700 mr-4 p-3 rounded-lg shadow-md">
              <div className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 text-purple-400 animate-spin" />
                <span className="text-sm text-gray-400">AI is thinking...</span>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      <div className="p-4 border-t border-gray-700">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
            placeholder={isConnected ? "Create a website, fix bugs, add features..." : "Connect to AI provider first..."}
            className="flex-1 bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all disabled:opacity-50"
            disabled={!isConnected}
          />
          <Button 
            size="sm" 
            onClick={handleSend} 
            disabled={isLoading || !isConnected || !input.trim()}
            className="bg-purple-600 hover:bg-purple-700 transition-colors disabled:opacity-50"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </Button>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Press Enter to send • Shift+Enter for new line
        </p>
      </div>
    </div>
  );
};
