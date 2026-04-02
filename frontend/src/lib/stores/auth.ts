import { writable } from 'svelte/store';
import { browser } from '$app/environment';

const API_URL = typeof import.meta.env.VITE_PUBLIC_API_URL !== 'undefined' 
    ? import.meta.env.VITE_PUBLIC_API_URL 
    : 'http://localhost:8080';

export interface User {
	id: string;
	email: string;
	role: 'admin' | 'user';
	theme: 'light' | 'dark' | 'system';
	primary_color: string;
	default_model: string;
	voice_enabled: boolean;
	status: string;
}

export interface AuthState {
	user: User | null;
	accessToken: string | null;
	refreshToken: string | null;
	loading: boolean;
}

const initialState: AuthState = {
	user: null,
	accessToken: null,
	refreshToken: null,
	loading: true
};

function createAuthStore() {
	const { subscribe, set, update } = writable<AuthState>(initialState);

	return {
		subscribe,
		set,
		update,
		async login(email: string, password: string) {
			update((state) => ({ ...state, loading: true }));
			try {
				const response = await fetch(`${API_URL}/api/auth/login`, {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({ email, password })
				});

				if (!response.ok) {
					throw new Error('Login failed');
				}

				const data = await response.json();

				if (browser) {
					localStorage.setItem('accessToken', data.access_token);
					localStorage.setItem('refreshToken', data.refresh_token);
				}

				const userResponse = await fetch(`${API_URL}/api/auth/me`, {
					headers: { Authorization: `Bearer ${data.access_token}` }
				});

				const user = await userResponse.json();

				set({
					user,
					accessToken: data.access_token,
					refreshToken: data.refresh_token,
					loading: false
				});

				return true;
			} catch (error) {
				update((state) => ({ ...state, loading: false }));
				return false;
			}
		},
		async signup(email: string, password: string) {
			update((state) => ({ ...state, loading: true }));
			try {
				const response = await fetch(`${API_URL}/api/auth/signup`, {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({ email, password })
				});

				if (!response.ok) {
					throw new Error('Signup failed');
				}

				const data = await response.json();

				set({
					user: {
						id: data.id,
						email: data.email,
						role: data.role,
						theme: 'dark',
						primary_color: '#7000FF',
						default_model: 'luigi-thinking',
						voice_enabled: false,
						status: 'active'
					},
					accessToken: data.api_key,
					refreshToken: null,
					loading: false
				});

				return { apiKey: data.api_key };
			} catch (error) {
				update((state) => ({ ...state, loading: false }));
				throw error;
			}
		},
		logout() {
			if (browser) {
				localStorage.removeItem('accessToken');
				localStorage.removeItem('refreshToken');
			}
			set(initialState);
		}
	};
}

export const authStore = createAuthStore();

export async function loadUser() {
	if (!browser) return;

	const token = localStorage.getItem('accessToken');
	if (!token) {
		authStore.update((state) => ({ ...state, loading: false }));
		return;
	}

	try {
		const response = await fetch(`${API_URL}/api/auth/me`, {
			headers: { Authorization: `Bearer ${token}` }
		});

		if (response.ok) {
			const user = await response.json();
			authStore.update((state) => ({
				...state,
				user,
				accessToken: token,
				loading: false
			}));
		} else {
			localStorage.removeItem('accessToken');
			localStorage.removeItem('refreshToken');
			authStore.update((state) => ({ ...state, loading: false }));
		}
	} catch {
		authStore.update((state) => ({ ...state, loading: false }));
	}
}
