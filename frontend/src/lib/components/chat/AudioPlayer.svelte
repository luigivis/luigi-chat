<script lang="ts">
	import { createEventDispatcher, onDestroy } from 'svelte';
	import { Play, Pause, Square, Volume2 } from 'lucide-svelte';

	export let src: string;
	export let autoplay = false;

	const dispatch = createEventDispatcher();

	let audio: HTMLAudioElement;
	let isPlaying = false;
	let duration = 0;
	let currentTime = 0;
	let volume = 1;

	function togglePlay() {
		if (isPlaying) {
			audio.pause();
		} else {
			audio.play();
		}
	}

	function stop() {
		audio.pause();
		audio.currentTime = 0;
		isPlaying = false;
	}

	function handleTimeUpdate() {
		currentTime = audio.currentTime;
	}

	function handleLoadedMetadata() {
		duration = audio.duration;
	}

	function handleEnded() {
		isPlaying = false;
		dispatch('ended');
	}

	function handleVolumeChange() {
		audio.volume = volume;
	}

	function formatTime(seconds: number): string {
		if (isNaN(seconds)) return '0:00';
		const mins = Math.floor(seconds / 60);
		const secs = Math.floor(seconds % 60);
		return `${mins}:${secs.toString().padStart(2, '0')}`;
	}

	onDestroy(() => {
		if (audio) {
			audio.pause();
		}
	});
</script>

<div class="flex items-center gap-3 p-3 bg-gray-800 rounded-lg">
	<button
		type="button"
		on:click={togglePlay}
		class="p-2 rounded-full bg-primary-600 hover:bg-primary-700 text-white transition"
	>
		{#if isPlaying}
			<Pause size={18} />
		{:else}
			<Play size={18} />
		{/if}
	</button>

	<button
		type="button"
		on:click={stop}
		class="p-2 rounded-full bg-gray-700 hover:bg-gray-600 text-white transition"
	>
		<Square size={18} />
	</button>

	<div class="flex-1 flex items-center gap-2">
		<Volume2 size={16} class="text-gray-400" />
		<input
			type="range"
			min="0"
			max="1"
			step="0.1"
			bind:value={volume}
			on:input={handleVolumeChange}
			class="w-20 h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer"
		/>
	</div>

	<span class="text-sm text-gray-400 font-mono">
		{formatTime(currentTime)} / {formatTime(duration)}
	</span>

	<audio
		bind:this={audio}
		{src}
		{autoplay}
		on:play={() => (isPlaying = true)}
		on:pause={() => (isPlaying = false)}
		on:timeupdate={handleTimeUpdate}
		on:loadedmetadata={handleLoadedMetadata}
		on:ended={handleEnded}
	/>
</div>