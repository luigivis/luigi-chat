<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { MessageCircle, Plus, Settings } from 'lucide-svelte';
	import type { Chat as ChatType } from '$lib/stores/chat';

	export let chats: ChatType[] = [];
	export let currentChatId: string | undefined = undefined;

	const dispatch = createEventDispatcher();

	function formatDate(dateStr: string | undefined): string {
		if (!dateStr) return '';
		const date = new Date(dateStr);
		return date.toLocaleDateString();
	}
</script>

<aside class="w-64 bg-gray-800 flex flex-col h-full">
	<div class="p-4 border-b border-gray-700">
		<button
			on:click={() => dispatch('newChat')}
			class="w-full flex items-center justify-center gap-2 bg-primary-600 hover:bg-primary-700 text-white py-2 px-4 rounded-lg transition"
		>
			<Plus size={18} />
			New Chat
		</button>
	</div>

	<nav class="flex-1 overflow-y-auto p-2">
		{#each chats as chat (chat.id)}
			<button
				on:click={() => dispatch('selectChat', chat.id)}
				class="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left mb-1 transition {chat.id === currentChatId ? 'bg-gray-700 text-white' : 'text-gray-400 hover:bg-gray-700 hover:text-white'}"
			>
				<MessageCircle size={18} />
				<span class="flex-1 truncate capitalize">{chat.title || 'New Chat'}</span>
				<span class="text-xs opacity-50">{formatDate(chat.updated_at)}</span>
			</button>
		{/each}

		{#if chats.length === 0}
			<div class="text-center text-gray-500 py-8">
				<p class="text-sm">No chats yet</p>
			</div>
		{/if}
	</nav>

	<div class="p-2 border-t border-gray-700">
		<a
			href="/workspace/settings"
			class="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-400 hover:bg-gray-700 hover:text-white transition"
		>
			<Settings size={18} />
			Settings
		</a>
	</div>
</aside>
