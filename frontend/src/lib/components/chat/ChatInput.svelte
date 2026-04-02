<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { Send, Image, Mic, Square } from 'lucide-svelte';

	export let disabled = false;

	let content = '';
	let imageUrls: string[] = [];
	let files: FileList | null = null;
	let isRecording = false;

	const dispatch = createEventDispatcher();

	function handleSubmit() {
		if (!content.trim() && imageUrls.length === 0) return;

		dispatch('send', { content: content.trim(), imageUrls });
		content = '';
		imageUrls = [];
		files = null;
	}

	function handleFileSelect() {
		if (!files) return;

		for (const file of files) {
			if (file.type.startsWith('image/')) {
				const reader = new FileReader();
				reader.onload = (e) => {
					imageUrls = [...imageUrls, e.target?.result as string];
				};
				reader.readAsDataURL(file);
			}
		}
	}

	function removeImage(index: number) {
		imageUrls = imageUrls.filter((_, i) => i !== index);
	}

	function handleKeyDown(e: KeyboardEvent) {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			handleSubmit();
		}
	}
</script>

<div class="border-t border-gray-800 bg-gray-900 p-4">
	{#if imageUrls.length > 0}
		<div class="flex gap-2 mb-3 flex-wrap">
			{#each imageUrls as url, i}
				<div class="relative">
					<img src={url} alt="Upload" class="w-20 h-20 object-cover rounded-lg" />
					<button
						type="button"
						on:click={() => removeImage(i)}
						class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs"
					>
						x
					</button>
				</div>
			{/each}
		</div>
	{/if}

	<form on:submit|preventDefault={handleSubmit} class="flex gap-3">
		<input
			type="file"
			accept="image/*"
			multiple
			bind:files
			on:change={handleFileSelect}
			class="hidden"
			id="file-input"
		/>

		<button
			type="button"
			on:click={() => document.getElementById('file-input')?.click()}
			class="p-3 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-white transition"
			disabled={disabled}
		>
			<Image size={20} />
		</button>

		<div class="flex-1 relative">
			<textarea
				bind:value={content}
				on:keydown={handleKeyDown}
				placeholder="Type your message..."
				rows="1"
				class="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 resize-none focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:opacity-50"
				disabled={disabled}
			></textarea>
		</div>

		<button
			type="submit"
			disabled={disabled || (!content.trim() && imageUrls.length === 0)}
			class="p-3 rounded-lg bg-primary-600 hover:bg-primary-700 text-white transition disabled:opacity-50 disabled:cursor-not-allowed"
		>
			{#if disabled}
				<Square size={20} />
			{:else}
				<Send size={20} />
			{/if}
		</button>
	</form>
</div>
