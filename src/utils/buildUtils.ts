// src/utils/buildUtils.ts

import { run_terminal_command } from '../types/default_api'; // Assuming default_api is in types

export const runBuildCommand = async (command: string): Promise<string> => {
  console.log(`Running build command: ${command}`);
  try {
    const result = await run_terminal_command({ command });
    console.log("Build command output:", result);
    // You might want to parse the result and return relevant information
    return JSON.stringify(result);
  } catch (error) {
    console.error("Error running build command:", error);
    throw error; // Re-throw the error for further handling
  }
};