
import React from 'react';
import { useProjectStore } from '@/stores/projectStore';
import { Button } from '@/components/ui/button';
import { Play, Save, FileText } from 'lucide-react';

export const CodeEditor = () => {
  const { files, currentFile, updateFile, saveProject } = useProjectStore();
  const currentContent = currentFile ? files[currentFile] || '' : '';

  const handleCodeChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    if (currentFile) {
      updateFile(currentFile, e.target.value);
    }
  };

  if (!currentFile) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-900">
        <div className="text-center">
          <FileText className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">Select a file to start editing</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-gray-900">
      <div className="h-12 bg-gray-800 border-b border-gray-700 flex items-center justify-between px-4">
        <span className="text-sm text-gray-300">{currentFile}</span>
        <div className="flex gap-2">
          <Button size="sm" variant="ghost" onClick={saveProject}>
            <Save className="w-4 h-4 mr-1" />
            Save
          </Button>
          <Button size="sm" variant="ghost">
            <Play className="w-4 h-4 mr-1" />
            Run
          </Button>
        </div>
      </div>

      <textarea
        value={currentContent}
        onChange={handleCodeChange}
        className="flex-1 bg-gray-900 text-gray-100 p-4 font-mono text-sm resize-none focus:outline-none"
        placeholder="Start coding..."
        spellCheck={false}
      />
    </div>
  );
};
