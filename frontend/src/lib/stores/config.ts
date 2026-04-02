import { writable } from 'svelte/store';

const API_URL = typeof import.meta.env.VITE_PUBLIC_API_URL !== 'undefined' 
    ? import.meta.env.VITE_PUBLIC_API_URL 
    : 'http://localhost:8080';

export const configStore = writable({
	WEBUI_NAME: 'Luigi Chat',
	PUBLIC_API_URL: API_URL
});
