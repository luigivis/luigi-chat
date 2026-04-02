<script lang="ts">
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth';

	let email = '';
	let password = '';
	let confirmPassword = '';
	let error = '';
	let loading = false;
	let apiKey = '';

	async function handleSubmit() {
		error = '';

		if (password !== confirmPassword) {
			error = 'Passwords do not match';
			return;
		}

		if (password.length < 6) {
			error = 'Password must be at least 6 characters';
			return;
		}

		loading = true;

		try {
			const result = await authStore.signup(email, password);
			apiKey = result.apiKey;
		} catch (e) {
			error = 'Signup failed. Email may already be in use.';
		} finally {
			loading = false;
		}
	}

	function copyApiKey() {
		navigator.clipboard.writeText(apiKey);
	}

	function goToChat() {
		goto('/');
	}
</script>

<div class="min-h-screen flex items-center justify-center bg-gray-900 px-4">
	<div class="max-w-md w-full space-y-8">
		<div class="text-center">
			<h1 class="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-primary-600">
				Luigi Chat
			</h1>
			<p class="mt-2 text-gray-400">Create your account</p>
		</div>

		{#if apiKey}
			<div class="bg-green-500/10 border border-green-500/50 text-green-400 px-4 py-6 rounded-lg">
				<h3 class="text-lg font-medium mb-2">Account Created!</h3>
				<p class="text-sm mb-4">Your API key has been generated. Save it securely - you won't be able to see it again.</p>
				
				<div class="flex gap-2">
					<input
						type="text"
						value={apiKey}
						readonly
						class="flex-1 bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm font-mono"
					/>
					<button
						on:click={copyApiKey}
						class="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm"
					>
						Copy
					</button>
				</div>

				<button
					on:click={goToChat}
					class="w-full mt-4 py-2 px-4 bg-primary-600 hover:bg-primary-700 rounded-lg text-white font-medium"
				>
					Go to Chat
				</button>
			</div>
		{:else}
			<form class="mt-8 space-y-6" on:submit|preventDefault={handleSubmit}>
				{#if error}
					<div class="bg-red-500/10 border border-red-500/50 text-red-400 px-4 py-3 rounded-lg">
						{error}
					</div>
				{/if}

				<div class="space-y-4">
					<div>
						<label for="email" class="sr-only">Email</label>
						<input
							id="email"
							type="email"
							bind:value={email}
							required
							class="appearance-none rounded-lg relative block w-full px-3 py-2 border border-gray-700 bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
							placeholder="Email address"
						/>
					</div>

					<div>
						<label for="password" class="sr-only">Password</label>
						<input
							id="password"
							type="password"
							bind:value={password}
							required
							class="appearance-none rounded-lg relative block w-full px-3 py-2 border border-gray-700 bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
							placeholder="Password (min 6 characters)"
						/>
					</div>

					<div>
						<label for="confirmPassword" class="sr-only">Confirm Password</label>
						<input
							id="confirmPassword"
							type="password"
							bind:value={confirmPassword}
							required
							class="appearance-none rounded-lg relative block w-full px-3 py-2 border border-gray-700 bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
							placeholder="Confirm password"
						/>
					</div>
				</div>

				<button
					type="submit"
					disabled={loading}
					class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
				>
					{#if loading}
						<svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
							<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
							<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
						</svg>
					{/if}
					Create Account
				</button>

				<div class="text-center text-sm text-gray-400">
					Already have an account? <a href="/auth/login" class="text-primary-400 hover:text-primary-300">Sign in</a>
				</div>
			</form>
		{/if}
	</div>
</div>
