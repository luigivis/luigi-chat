<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { authStore, loadUser } from '$lib/stores/auth';

	let loading = true;

	onMount(async () => {
		await loadUser();
		loading = false;

		const publicRoutes = ['/auth/login', '/auth/signup'];
		const isPublicRoute = publicRoutes.some((route) => $page.url.pathname.startsWith(route));

		if (!$authStore.user && !isPublicRoute) {
			goto('/auth/login');
		}
	});
</script>

{#if loading}
	<div class="flex items-center justify-center h-screen">
		<div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
	</div>
{:else}
	<slot />
{/if}
