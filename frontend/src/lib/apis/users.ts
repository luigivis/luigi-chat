import { API_URL, getAuthHeaders, handleResponse } from './index';

export interface User {
	id: string;
	email: string;
	role: string;
	theme: string;
	primary_color: string;
	default_model: string;
	voice_enabled: boolean;
	status: string;
	litellm_key?: string;
	total_spend?: number;
	key_spend?: number;
}

export interface CreateUserRequest {
	email: string;
	password: string;
	role?: string;
}

export interface UpdateUserRequest {
	theme?: string;
	primary_color?: string;
	font_size?: string;
	compact_mode?: boolean;
	default_model?: string;
	voice_enabled?: boolean;
	voice_id?: string;
	speech_speed?: string;
	speech_emotion?: string;
	status?: string;
	role?: string;
}

export async function getUsers(): Promise<User[]> {
	const response = await fetch(`${API_URL}/api/users/`, {
		headers: getAuthHeaders()
	});
	return handleResponse<User[]>(response);
}

export async function getUser(userId: string): Promise<User> {
	const response = await fetch(`${API_URL}/api/users/${userId}`, {
		headers: getAuthHeaders()
	});
	return handleResponse<User>(response);
}

export async function createUser(request: CreateUserRequest): Promise<User> {
	const response = await fetch(`${API_URL}/api/users/`, {
		method: 'POST',
		headers: getAuthHeaders(),
		body: JSON.stringify(request)
	});
	return handleResponse<User>(response);
}

export async function updateUser(userId: string, request: UpdateUserRequest): Promise<User> {
	const response = await fetch(`${API_URL}/api/users/${userId}`, {
		method: 'PATCH',
		headers: getAuthHeaders(),
		body: JSON.stringify(request)
	});
	return handleResponse<User>(response);
}

export async function deleteUser(userId: string): Promise<void> {
	const response = await fetch(`${API_URL}/api/users/${userId}`, {
		method: 'DELETE',
		headers: getAuthHeaders()
	});
	if (!response.ok) throw new Error('Failed to delete user');
}