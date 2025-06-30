
import { create } from 'zustand';

interface ProjectState {
  projectName: string;
  files: Record<string, string>;
  currentFile: string | null;
  previewContent: string;
  setProjectName: (name: string) => void;
  addFile: (fileName: string, content: string) => void;
  updateFile: (fileName: string, content: string) => void;
  deleteFile: (fileName: string) => void;
  setCurrentFile: (fileName: string | null) => void;
  generatePreview: () => void;
  saveProject: () => void;
}

export const useProjectStore = create<ProjectState>((set, get) => ({
  projectName: 'New Project',
  files: {
    'index.html': `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My App</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
            max-width: 500px;
        }
        h1 {
            color: #333;
            margin-bottom: 1rem;
        }
        p {
            color: #666;
            line-height: 1.6;
        }
        .btn {
            background: #667eea;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 1rem;
            transition: background 0.3s;
        }
        .btn:hover {
            background: #5a6fd8;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to Bolt Clone</h1>
        <p>This is your new web application created with AI assistance.</p>
        <button class="btn" onclick="alert('Hello from your AI-generated app!')">
            Click Me!
        </button>
    </div>
</body>
</html>`,
    'style.css': `/* Add your custom styles here */
body {
    font-family: Arial, sans-serif;
}`,
    'script.js': `// Add your JavaScript code here
console.log('Hello from Bolt Clone!');`,
  },
  currentFile: 'index.html',
  previewContent: '',

  setProjectName: (name) => set({ projectName: name }),

  addFile: (fileName, content) =>
    set((state) => ({
      files: { ...state.files, [fileName]: content },
      currentFile: fileName,
    })),

  updateFile: (fileName, content) =>
    set((state) => ({
      files: { ...state.files, [fileName]: content },
    })),

  deleteFile: (fileName) =>
    set((state) => {
      const newFiles = { ...state.files };
      delete newFiles[fileName];
      const currentFile = state.currentFile === fileName ? null : state.currentFile;
      return { files: newFiles, currentFile };
    }),

  setCurrentFile: (fileName) => set({ currentFile: fileName }),

  generatePreview: () => {
    const state = get();
    const htmlFile = state.files['index.html'] || '';
    const cssFile = state.files['style.css'] || '';
    const jsFile = state.files['script.js'] || '';

    let preview = htmlFile;

    // Inject CSS if exists
    if (cssFile && !preview.includes('<style>')) {
      preview = preview.replace('</head>', `<style>${cssFile}</style></head>`);
    }

    // Inject JS if exists
    if (jsFile && !preview.includes('<script>')) {
      preview = preview.replace('</body>', `<script>${jsFile}</script></body>`);
    }

    set({ previewContent: preview });
  },

  saveProject: () => {
    const state = get();
    const projectData = {
      name: state.projectName,
      files: state.files,
      timestamp: new Date().toISOString(),
    };
    
    localStorage.setItem('bolt-clone-project', JSON.stringify(projectData));
    console.log('Project saved!');
  },
}));
