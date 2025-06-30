
import React, { useEffect, useRef } from 'react';
import { useProjectStore } from '@/stores/projectStore';
import { Button } from '@/components/ui/button';
import { RefreshCw, ExternalLink } from 'lucide-react';

export const Preview = () => {
  const { files, previewContent, generatePreview } = useProjectStore();
  const iframeRef = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    generatePreview();
  }, [files, generatePreview]);

  const refreshPreview = () => {
    generatePreview();
    if (iframeRef.current) {
      iframeRef.current.src = iframeRef.current.src;
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-gray-900">
      <div className="h-12 bg-gray-800 border-b border-gray-700 flex items-center justify-between px-4">
        <span className="text-sm text-gray-300">Preview</span>
        <div className="flex gap-2">
          <Button size="sm" variant="ghost" onClick={refreshPreview}>
            <RefreshCw className="w-4 h-4 mr-1" />
            Refresh
          </Button>
          <Button size="sm" variant="ghost">
            <ExternalLink className="w-4 h-4 mr-1" />
            Open
          </Button>
        </div>
      </div>

      <div className="flex-1 bg-white">
        <iframe
          ref={iframeRef}
          srcDoc={previewContent}
          className="w-full h-full border-0"
          sandbox="allow-scripts allow-same-origin"
        />
      </div>
    </div>
  );
};
