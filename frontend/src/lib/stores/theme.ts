import { writable } from 'svelte/store';
import { browser } from '$app/environment';

export type Theme = 'light' | 'dark' | 'system';

export interface ThemeState {
	theme: Theme;
	primaryColor: string;
	fontSize: 'small' | 'medium' | 'large';
	compactMode: boolean;
	sidebarCollapsed: boolean;
}

const defaultState: ThemeState = {
	theme: 'dark',
	primaryColor: '#7000FF',
	fontSize: 'medium',
	compactMode: false,
	sidebarCollapsed: false
};

function createThemeStore() {
	const { subscribe, set, update } = writable<ThemeState>(defaultState);

	function applyTheme(state: ThemeState) {
		if (!browser) return;

		const root = document.documentElement;

		if (state.theme === 'system') {
			const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
			root.classList.toggle('dark', isDark);
		} else {
			root.classList.toggle('dark', state.theme === 'dark');
		}

		root.style.setProperty('--primary', state.primaryColor);

		localStorage.setItem('theme', JSON.stringify(state));
	}

	return {
		subscribe,
		set: (state: ThemeState) => {
			set(state);
			applyTheme(state);
		},
		update: (fn: (state: ThemeState) => ThemeState) => {
			update((state) => {
				const newState = fn(state);
				applyTheme(newState);
				return newState;
			});
		},
		init() {
			if (!browser) return;

			const stored = localStorage.getItem('theme');
			if (stored) {
				try {
					const state = JSON.parse(stored);
					set(state);
					applyTheme(state);
				} catch {
					set(defaultState);
					applyTheme(defaultState);
				}
			}
		},
		setTheme(theme: Theme) {
			update((state) => ({ ...state, theme }));
		},
		setPrimaryColor(color: string) {
			update((state) => ({ ...state, primaryColor: color }));
		},
		toggleSidebar() {
			update((state) => ({ ...state, sidebarCollapsed: !state.sidebarCollapsed }));
		}
	};
}

export const themeStore = createThemeStore();
