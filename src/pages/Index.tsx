
import React from 'react';
import { Header } from '@/components/Header';
import { Sidebar } from '@/components/Sidebar';
import { CodeEditor } from '@/components/CodeEditor';
import { Preview } from '@/components/Preview';
import { ChatPanel } from '@/components/ChatPanel';
import { useOllama } from '@/hooks/useOllama';
import { useProjectStore } from '@/stores/projectStore';

const Index = () => {
  const { models, selectedModel, isConnected } = useOllama();
  const { currentFile } = useProjectStore();

  return (
    <div className="h-screen bg-gray-900 text-white flex flex-col overflow-hidden">
      <Header />
      
      <div className="flex-1 flex overflow-hidden">
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
      </div>
      
      {!isConnected && (
        <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
          <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
            <h3 className="text-lg font-semibold mb-2">Connecting to Ollama</h3>
            <p className="text-gray-400">Make sure Ollama is running on localhost:11434</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Index;
