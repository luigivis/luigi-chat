import { API_URL, getAuthHeaders, handleResponse } from './index';

export interface SpeechRequest {
	input: string;
	model?: string;
	voice_id?: string;
	speed?: number;
	emotion?: string;
	format?: string;
}

export interface Voice {
	id: string;
	name: string;
	gender: string;
}

export interface VoicesResponse {
	voices: Voice[];
}

export async function textToSpeech(request: SpeechRequest): Promise<{ audio_url: string }> {
	const response = await fetch(`${API_URL}/api/audio/speech`, {
		method: 'POST',
		headers: getAuthHeaders(),
		body: JSON.stringify(request)
	});
	return handleResponse(response);
}

export async function listVoices(): Promise<VoicesResponse> {
	const response = await fetch(`${API_URL}/api/audio/voices`, {
		headers: getAuthHeaders()
	});
	return handleResponse(response);
}