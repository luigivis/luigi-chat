<script lang="ts">
	import type { Message } from '$lib/stores/chat';

	export let message: Message;
</script>

<div class="flex {message.role === 'user' ? 'justify-end' : 'justify-start'}">
	<div class="max-w-[70%] rounded-lg px-4 py-3 {message.role === 'user' ? 'bg-primary-600 text-white' : 'bg-gray-800 text-white'}">
		{#if message.image_urls && message.image_urls.length > 0}
			<div class="flex gap-2 mb-2 flex-wrap">
				{#each message.image_urls as url}
					<img src={url} alt="Uploaded" class="max-w-64 max-h-64 rounded object-contain" />
				{/each}
			</div>
		{/if}

		<div class="whitespace-pre-wrap break-words">
			{message.content}
		</div>

		<div class="text-xs mt-1 opacity-70">
			{message.model || message.role}
		</div>
	</div>
</div>
