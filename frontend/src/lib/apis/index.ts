const API_URL = typeof import.meta.env.VITE_PUBLIC_API_URL !== 'undefined' 
    ? import.meta.env.VITE_PUBLIC_API_URL 
    : 'http://localhost:8080';

export { API_URL };

export function getAuthHeaders() {
	if (typeof window === 'undefined') return {};

	const token = localStorage.getItem('accessToken');
	return {
		Authorization: `Bearer ${token}`,
		'Content-Type': 'application/json'
	};
}

export async function handleResponse<T>(response: Response): Promise<T> {
	if (!response.ok) {
		const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
		throw new Error(error.detail || `HTTP ${response.status}`);
	}
	return response.json();
}
