<script lang="ts">
	import type { Message } from '$lib/stores/chat';
	import MessageBubble from './Message.svelte';

	export let messages: Message[] = [];
	export let streaming = false;
</script>

<div class="flex-1 overflow-y-auto px-4 py-6">
	{#if messages.length === 0}
		<div class="flex flex-col items-center justify-center h-full text-gray-500">
			<div class="text-6xl mb-4">💬</div>
			<p class="text-lg">Start a conversation</p>
			<p class="text-sm mt-1">Send a message to begin chatting</p>
		</div>
	{:else}
		<div class="space-y-4 max-w-4xl mx-auto">
			{#each messages as message (message.id)}
				<MessageBubble {message} />
			{/each}

			{#if streaming}
				<div class="flex justify-start">
					<div class="bg-gray-800 rounded-lg px-4 py-3">
						<div class="flex gap-1">
							<div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
							<div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
							<div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
						</div>
					</div>
				</div>
			{/if}
		</div>
	{/if}
</div>
