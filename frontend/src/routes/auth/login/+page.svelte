<script lang="ts">
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth';

	let email = '';
	let password = '';
	let error = '';
	let loading = false;

	async function handleSubmit() {
		error = '';
		loading = true;

		try {
			const success = await authStore.login(email, password);
			if (success) {
				goto('/');
			} else {
				error = 'Invalid email or password';
			}
		} catch (e) {
			error = 'Login failed. Please try again.';
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>Sign In - Luigi Chat</title>
	<meta name="description" content="Sign in to your Luigi Chat account to access AI-powered chat with MiniMax models." />
	<meta name="robots" content="noindex, nofollow" />
	<meta property="og:title" content="Sign In - Luigi Chat" />
	<meta property="og:description" content="Access your Luigi Chat account and start chatting with AI models." />
	<meta property="og:type" content="website" />
	<meta name="twitter:card" content="summary" />
	<meta name="twitter:title" content="Sign In - Luigi Chat" />
	<meta name="twitter:description" content="Sign in to your Luigi Chat account." />
</svelte:head>

<div class="min-h-screen flex items-center justify-center bg-gray-900 px-4">
	<div class="max-w-md w-full space-y-8">
		<div class="text-center">
			<h1 class="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-primary-600">
				Luigi Chat
			</h1>
			<p class="mt-2 text-gray-400">Sign in to your account</p>
		</div>

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
						placeholder="Password"
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
				Sign in
			</button>

			<div class="text-center text-sm text-gray-400">
				Don't have an account? <a href="/auth/signup" class="text-primary-400 hover:text-primary-300">Sign up</a>
			</div>
		</form>
	</div>
</div>
