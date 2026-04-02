<script lang="ts">
	import { themeStore } from '$lib/stores/theme';
	import { authStore } from '$lib/stores/auth';
	import { goto } from '$app/navigation';

	let theme = 'dark';
	let primaryColor = '#7000FF';

	async function handleThemeChange(newTheme: string) {
		themeStore.setTheme(newTheme as 'light' | 'dark' | 'system');
		theme = newTheme;
	}

	async function handleColorChange(e: Event) {
		const target = e.target as HTMLInputElement;
		primaryColor = target.value;
		themeStore.setPrimaryColor(primaryColor);
	}

	async function handleSavePreferences() {
		// TODO: Call API to save preferences
		alert('Preferences saved!');
	}

	function handleLogout() {
		authStore.logout();
		goto('/auth/login');
	}
</script>

<div class="p-6 max-w-2xl mx-auto">
	<h1 class="text-2xl font-bold mb-6">Settings</h1>

	<div class="space-y-6">
		<section class="bg-gray-800 rounded-lg p-6">
			<h2 class="text-lg font-semibold mb-4">Theme</h2>

			<div class="flex gap-4 mb-4">
				<button
					on:click={() => handleThemeChange('light')}
					class="flex-1 py-3 rounded-lg border-2 transition {theme === 'light' ? 'border-primary-500 bg-gray-700' : 'border-gray-600 hover:border-gray-500'}"
				>
					Light
				</button>
				<button
					on:click={() => handleThemeChange('dark')}
					class="flex-1 py-3 rounded-lg border-2 transition {theme === 'dark' ? 'border-primary-500 bg-gray-700' : 'border-gray-600 hover:border-gray-500'}"
				>
					Dark
				</button>
				<button
					on:click={() => handleThemeChange('system')}
					class="flex-1 py-3 rounded-lg border-2 transition {theme === 'system' ? 'border-primary-500 bg-gray-700' : 'border-gray-600 hover:border-gray-500'}"
				>
					System
				</button>
			</div>

			<div>
				<label class="block text-sm text-gray-400 mb-2">Primary Color</label>
				<input
					type="color"
					value={primaryColor}
					on:input={handleColorChange}
					class="w-full h-12 rounded-lg cursor-pointer"
				/>
			</div>
		</section>

		<section class="bg-gray-800 rounded-lg p-6">
			<h2 class="text-lg font-semibold mb-4">Account</h2>

			{#if $authStore.user}
				<div class="space-y-3">
					<div>
						<span class="text-gray-400">Email:</span>
						<span class="ml-2">{$authStore.user.email}</span>
					</div>
					<div>
						<span class="text-gray-400">Role:</span>
						<span class="ml-2 capitalize">{$authStore.user.role}</span>
					</div>
				</div>
			{/if}

			<button
				on:click={handleLogout}
				class="mt-4 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition"
			>
				Logout
			</button>
		</section>
	</div>
</div>
