<script lang="ts">
	import { onMount } from 'svelte';
	import { chatStore, type Message } from '$lib/stores/chat';
	import { authStore } from '$lib/stores/auth';
	import * as chatApi from '$lib/apis/chats';
	import ChatInput from '$lib/components/chat/ChatInput.svelte';
	import Messages from '$lib/components/chat/Messages.svelte';
	import Sidebar from '$lib/components/layout/Sidebar.svelte';
	import Header from '$lib/components/layout/Header.svelte';

	let loading = true;
	let selectedModel = 'luigi-thinking';

	onMount(async () => {
		await loadChats();
		loading = false;
	});

	async function loadChats() {
		try {
			const chats = await chatApi.getChats();
			chatStore.setChats(chats);
		} catch (error) {
			console.error('Failed to load chats:', error);
		}
	}

	async function handleNewChat() {
		try {
			const chat = await chatApi.createChat('New Chat', selectedModel);
			chatStore.setCurrentChat(chat);
			chatStore.setMessages([]);
			await loadChats();
		} catch (error) {
			console.error('Failed to create chat:', error);
		}
	}

	async function handleSelectChat(chatId: string) {
		try {
			const chat = await chatApi.getChat(chatId);
			const messages = await chatApi.getMessages(chatId);
			chatStore.setCurrentChat(chat);
			chatStore.setMessages(messages);
			selectedModel = chat.model;
		} catch (error) {
			console.error('Failed to load chat:', error);
		}
	}

	async function handleSendMessage(content: string, imageUrls: string[]) {
		if (!$chatStore.currentChat) {
			await handleNewChat();
		}

		const chatId = $chatStore.currentChat?.id;
		if (!chatId) return;

		const userMessage: Message = {
			id: crypto.randomUUID(),
			role: 'user',
			content,
			image_urls: imageUrls,
			model: selectedModel,
			created_at: new Date().toISOString()
		};

		chatStore.addMessage(userMessage);
		chatStore.setStreaming(true);

		try {
			const response = await chatApi.sendMessage(
				chatId,
				content,
				imageUrls,
				selectedModel,
				true
			);

			if (response.body) {
				const reader = response.body.getReader();
				const decoder = new TextDecoder();
				let assistantContent = '';

				const assistantMessageId = crypto.randomUUID();
				chatStore.addMessage({
					id: assistantMessageId,
					role: 'assistant',
					content: '',
					created_at: new Date().toISOString()
				});

				while (true) {
					const { done, value } = await reader.read();
					if (done) break;

					const chunk = decoder.decode(value);
					const lines = chunk.split('\n');

					for (const line of lines) {
						if (line.startsWith('data: ')) {
							const data = line.slice(6);
							if (data === '[DONE]') continue;

							try {
								const parsed = JSON.parse(data);
								const delta = parsed.choices?.[0]?.delta?.content;
								if (delta) {
									assistantContent += delta;
									chatStore.updateMessage(assistantMessageId, assistantContent);
								}
							} catch {}
						}
					}
				}
			}

			const messages = await chatApi.getMessages(chatId);
			chatStore.setMessages(messages);
		} catch (error) {
			console.error('Failed to send message:', error);
		} finally {
			chatStore.setStreaming(false);
		}
	}

	function handleModelChange(model: string) {
		selectedModel = model;
	}
</script>

<div class="flex h-screen bg-gray-900">
	<Sidebar
		chats={$chatStore.chats}
		currentChatId={$chatStore.currentChat?.id}
		on:newChat={handleNewChat}
		on:selectChat={(e) => handleSelectChat(e.detail)}
	/>

	<div class="flex-1 flex flex-col">
		<Header
			user={$authStore.user}
			{selectedModel}
			on:modelChange={(e) => handleModelChange(e.detail)}
			on:logout={() => authStore.logout()}
		/>

		<main class="flex-1 overflow-hidden">
			{#if loading}
				<div class="flex items-center justify-center h-full">
					<div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
				</div>
			{:else}
				<div class="h-full flex flex-col">
					<Messages messages={$chatStore.messages} streaming={$chatStore.streaming} />
					<ChatInput
						on:send={(e) => handleSendMessage(e.detail.content, e.detail.imageUrls)}
						disabled={$chatStore.streaming}
					/>
				</div>
			{/if}
		</main>
	</div>
</div>
