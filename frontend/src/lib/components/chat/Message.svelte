<script lang="ts">
	import type { Message } from '$lib/stores/chat';
	import { createEventDispatcher } from 'svelte';
	import { Volume2 } from 'lucide-svelte';
	import AudioPlayer from './AudioPlayer.svelte';
	import { textToSpeech } from '$lib/apis/audio';

	export let message: Message;

	const dispatch = createEventDispatcher();

	let audioUrl: string | null = null;
	let loadingAudio = false;
	let showPlayer = false;

	async function playTTS() {
		if (!message.content || message.role !== 'assistant') return;

		loadingAudio = true;
		try {
			const data = await textToSpeech({
				input: message.content,
				model: 'luigi-voice'
			});
			audioUrl = data.audio_url;
			showPlayer = true;
		} catch (error) {
			console.error('TTS error:', error);
		} finally {
			loadingAudio = false;
		}
	}

	function handleAudioEnded() {
		showPlayer = false;
		audioUrl = null;
	}
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

		<div class="flex items-center justify-between mt-2">
			<span class="text-xs opacity-70">
				{message.model || message.role}
			</span>

			{#if message.role === 'assistant' && message.content}
				<button
					type="button"
					on:click={playTTS}
					disabled={loadingAudio}
					class="p-1.5 rounded hover:bg-gray-700 text-gray-400 hover:text-white transition disabled:opacity-50"
					title="Play TTS"
				>
					{#if loadingAudio}
						<span class="text-xs animate-pulse">...</span>
					{:else}
						<Volume2 size={16} />
					{/if}
				</button>
			{/if}
		</div>

		{#if showPlayer && audioUrl}
			<div class="mt-3">
				<AudioPlayer src={audioUrl} on:ended={handleAudioEnded} />
			</div>
		{/if}
	</div>
</div>