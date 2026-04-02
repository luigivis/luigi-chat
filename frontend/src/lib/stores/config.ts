import { writable } from 'svelte/store';

export const configStore = writable({
	WEBUI_NAME: 'Luigi Chat',
	PUBLIC_API_URL: 'http://localhost:8080'
});
