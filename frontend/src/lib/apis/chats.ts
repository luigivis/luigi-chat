import { API_URL, getAuthHeaders, handleResponse } from './index';
import type { Chat, Message } from '$lib/stores/chat';

export async function getChats(): Promise<Chat[]> {
	const response = await fetch(`${API_URL}/chats/`, {
		headers: getAuthHeaders()
	});
	return handleResponse<Chat[]>(response);
}

export async function createChat(title?: string, model?: string): Promise<Chat> {
	const response = await fetch(`${API_URL}/chats/`, {
		method: 'POST',
		headers: getAuthHeaders(),
		body: JSON.stringify({ title, model })
	});
	return handleResponse<Chat>(response);
}

export async function getChat(chatId: string): Promise<Chat> {
	const response = await fetch(`${API_URL}/chats/${chatId}`, {
		headers: getAuthHeaders()
	});
	return handleResponse<Chat>(response);
}

export async function getMessages(chatId: string): Promise<Message[]> {
	const response = await fetch(`${API_URL}/chats/${chatId}/messages`, {
		headers: getAuthHeaders()
	});
	return handleResponse<Message[]>(response);
}

export async function sendMessage(
	chatId: string,
	content: string,
	imageUrls: string[] = [],
	model?: string,
	stream: boolean = true
): Promise<Response> {
	const response = await fetch(`${API_URL}/chats/${chatId}/messages`, {
		method: 'POST',
		headers: {
			...getAuthHeaders(),
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({ content, image_urls: imageUrls, model, stream })
	});
	return response;
}

export async function deleteChat(chatId: string): Promise<void> {
	const response = await fetch(`${API_URL}/chats/${chatId}`, {
		method: 'DELETE',
		headers: getAuthHeaders()
	});
	if (!response.ok) throw new Error('Failed to delete chat');
}

export async function updateChat(
	chatId: string,
	data: { title?: string; model?: string; tags?: string[] }
): Promise<Chat> {
	const response = await fetch(`${API_URL}/chats/${chatId}`, {
		method: 'PATCH',
		headers: getAuthHeaders(),
		body: JSON.stringify(data)
	});
	return handleResponse<Chat>(response);
}
