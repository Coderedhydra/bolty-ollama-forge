// src/lib/ollama.ts

export async function generateWebsiteCode(prompt: string): Promise<{ name: string; language: string; content: string }[]> {
  console.log("Received prompt for website generation:", prompt);

  const ollamaUrl = 'http://localhost:11434/api/generate'; // Default Ollama API endpoint
  const model = 'llama2'; // Replace with the model you want to use

  try {
    const response = await fetch(ollamaUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ model, prompt }),
    });

    if (!response.ok) {
      throw new Error(`Ollama API request failed with status: ${response.status}`);
    }
    const data = await response.json();
    console.log("Ollama API response:", data);

    // Assuming the response has a 'files' array with objects like { name, language, content }
    if (data && data.files && Array.isArray(data.files)) {
      // data.files.forEach((file: { name: string; language: string; content: string }) => {
      //   console.log(`File: ${file.name}, Content:\n${file.content}`);
      // });
      // Return the files array
 return data.files;
    }
  } catch (error) {
    console.error("Error calling Ollama API:", error);
  }
  // Return an empty array if no files are found or an error occurs
 return [];
}