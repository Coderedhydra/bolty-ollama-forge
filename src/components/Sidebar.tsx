
import React from 'react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useProjectStore } from '@/stores/projectStore';
import { FileText, Folder, Plus, Trash2 } from 'lucide-react';

export const Sidebar = () => {
  const { files, currentFile, addFile, deleteFile, setCurrentFile } = useProjectStore();

  const handleAddFile = () => {
    const fileName = prompt('Enter file name:');
    if (fileName) {
      addFile(fileName, '');
    }
  };

  return (
    <div className="w-64 bg-gray-800 border-r border-gray-700 flex flex-col">
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-gray-300">Project Files</h2>
          <Button size="sm" variant="ghost" onClick={handleAddFile}>
            <Plus className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-2">
          {Object.entries(files).map(([fileName, content]) => (
            <div
              key={fileName}
              className={`flex items-center justify-between p-2 rounded cursor-pointer hover:bg-gray-700 ${
                currentFile === fileName ? 'bg-gray-700 border-l-2 border-purple-400' : ''
              }`}
              onClick={() => setCurrentFile(fileName)}
            >
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-gray-400" />
                <span className="text-sm text-gray-300">{fileName}</span>
              </div>
              <Button
                size="sm"
                variant="ghost"
                onClick={(e) => {
                  e.stopPropagation();
                  deleteFile(fileName);
                }}
              >
                <Trash2 className="w-3 h-3 text-gray-500" />
              </Button>
            </div>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
};
