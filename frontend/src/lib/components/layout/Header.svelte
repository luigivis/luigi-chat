<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { LogOut, ChevronDown, Bot, Sparkles } from 'lucide-svelte';
	import type { User } from '$lib/stores/auth';

	export let user: User | null = null;
	export let selectedModel = 'luigi-thinking';

	const dispatch = createEventDispatcher();

	const models = [
		{ id: 'luigi-thinking', name: 'MiniMax M2.7', icon: Bot },
		{ id: 'luigi-vision', name: 'MiniMax Text-01', icon: Sparkles }
	];

	function getCurrentModelInfo() {
		return models.find((m) => m.id === selectedModel) || models[0];
	}
</script>

<header class="bg-gray-800 border-b border-gray-700 px-4 py-3">
	<div class="flex items-center justify-between">
		<div class="flex items-center gap-4">
			<h1 class="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-primary-600">
				Luigi Chat
			</h1>

			<div class="relative">
				<select
					value={selectedModel}
					on:change={(e) => dispatch('modelChange', e.currentTarget.value)}
					class="appearance-none bg-gray-700 text-white px-3 py-1.5 pr-8 rounded-lg text-sm cursor-pointer focus:outline-none focus:ring-2 focus:ring-primary-500"
				>
					{#each models as model}
						<option value={model.id}>{model.name}</option>
					{/each}
				</select>
				<ChevronDown size={14} class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
			</div>
		</div>

		<div class="flex items-center gap-4">
			{#if user}
				<span class="text-sm text-gray-400">{user.email}</span>
				<span class="px-2 py-1 bg-gray-700 rounded text-xs text-gray-300">{user.role}</span>
			{/if}

			<button
				on:click={() => dispatch('logout')}
				class="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition"
				title="Logout"
			>
				<LogOut size={18} />
			</button>
		</div>
	</div>
</header>
