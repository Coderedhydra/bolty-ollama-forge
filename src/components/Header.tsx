
import React from 'react';
import { useProjectStore } from '@/stores/projectStore';
import { AIProviderSelector } from '@/components/AIProviderSelector';
import { Bolt } from 'lucide-react';

export const Header = () => {
  const { projectName, setProjectName } = useProjectStore();

  return (
    <header className="h-14 bg-gray-800 border-b border-gray-700 flex items-center justify-between px-4">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <Bolt className="w-6 h-6 text-purple-400" />
          <span className="text-xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
            Bolt Clone
          </span>
        </div>
        
        <input
          type="text"
          value={projectName}
          onChange={(e) => setProjectName(e.target.value)}
          className="bg-gray-700 border border-gray-600 rounded px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
          placeholder="Project name"
        />
      </div>

      <AIProviderSelector />
    </header>
  );
};
