// src/renderer/services/SttService.ts

export const SttService = {
  /**
   * Transcribes an audio blob by sending it to the main process.
   * @param audioBlob The audio data to transcribe.
   * @returns A promise that resolves with the transcription text.
   * @throws Will throw an error if the transcription fails or the service is unavailable.
   */
  transcribe: async (audioBlob: Blob): Promise<string> => {
    if (window.electronAPI && window.electronAPI.sttTranscribe) {
      try {
        // 1. Convert Blob to ArrayBuffer
        const arrayBuffer = await audioBlob.arrayBuffer();
        // 2. Convert ArrayBuffer to Uint8Array, which is transferable via IPC
        const audioData = new Uint8Array(arrayBuffer);
        
        // 3. Send the Uint8Array and await the response
        const response = await window.electronAPI.sttTranscribe(audioData);
        return response;
        
      } catch (error) {
        // Log the error for debugging purposes
        console.error('Error calling STT service via IPC:', error);
        // Re-throw the error to be handled by the calling function
        throw error;
      }
    }
    
    // If the service is not available, throw a consistent error.
    throw new Error('STT service is not available.');
  },
};