
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useAIProviders } from '@/hooks/useAIProviders';
import { useProjectStore } from '@/stores/projectStore';
import { Send, MessageSquare, Code, Bug, Sparkles, FileText } from 'lucide-react';

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export const ChatPanel = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { generateCode, isConnected } = useAIProviders();
  const { files, addFile, updateFile, currentFile, generatePreview } = useProjectStore();

  const handleSend = async () => {
    if (!input.trim() || !isConnected) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
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
      response.files.forEach(file => {
        addFile(file.fileName, file.content);
      });

      // Generate preview after adding files
      generatePreview();

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: `${response.explanation}\n\nGenerated files:\n${response.files.map(f => `• ${f.fileName}`).join('\n')}\n\nSuggestions:\n${response.suggestions.map(s => `• ${s}`).join('\n')}`,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error generating code:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: `Error: ${error instanceof Error ? error.message : 'Failed to generate code'}`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickAction = (action: string) => {
    setInput(action);
  };

  const handleFixBugs = async () => {
    if (!currentFile || !isConnected) return;

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

        const assistantMessage: ChatMessage = {
          id: Date.now().toString(),
          type: 'assistant',
          content: `Fixed bugs in ${fixedFile.fileName}:\n${response.explanation}`,
          timestamp: new Date(),
        };

        setMessages(prev => [...prev, assistantMessage]);
      }
    } catch (error) {
      console.error('Error fixing bugs:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-80 bg-gray-800 border-l border-gray-700 flex flex-col">
      <div className="p-4 border-b border-gray-700">
        <h2 className="text-sm font-semibold text-gray-300 mb-4">AI Assistant</h2>
        
        <div className="grid grid-cols-2 gap-2 mb-4">
          <Button
            size="sm"
            variant="outline"
            onClick={() => handleQuickAction('Create a modern landing page')}
          >
            <Code className="w-3 h-3 mr-1" />
            Generate
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={handleFixBugs}
            disabled={!currentFile || isLoading}
          >
            <Bug className="w-3 h-3 mr-1" />
            Fix Bugs
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => handleQuickAction('Create a React component')}
          >
            <Sparkles className="w-3 h-3 mr-1" />
            Component
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => handleQuickAction('Add responsive design')}
          >
            <FileText className="w-3 h-3 mr-1" />
            Responsive
          </Button>
        </div>

        {!isConnected && (
          <div className="text-xs text-amber-400 bg-amber-400/10 p-2 rounded">
            Please select and connect to an AI provider
          </div>
        )}
      </div>

      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`p-3 rounded-lg ${
                message.type === 'user'
                  ? 'bg-purple-600 ml-4'
                  : 'bg-gray-700 mr-4'
              }`}
            >
              <p className="text-sm text-white whitespace-pre-wrap">
                {message.content}
              </p>
              <span className="text-xs text-gray-400 mt-2 block">
                {message.timestamp.toLocaleTimeString()}
              </span>
            </div>
          ))}
          
          {isLoading && (
            <div className="bg-gray-700 mr-4 p-3 rounded-lg">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse" />
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
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Create a website, fix bugs, add features..."
            className="flex-1 bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
            disabled={!isConnected}
          />
          <Button size="sm" onClick={handleSend} disabled={isLoading || !isConnected}>
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
};
