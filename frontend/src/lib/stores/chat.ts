import { writable } from 'svelte/store';

export interface Message {
	id: string;
	role: 'user' | 'assistant' | 'system';
	content: string;
	image_urls?: string[];
	model?: string;
	tokens_used?: number;
	created_at: string;
}

export interface Chat {
	id: string;
	user_id: string;
	title: string;
	model: string;
	tags: string[];
	created_at: string;
	updated_at: string;
}

export interface ChatState {
	chats: Chat[];
	currentChat: Chat | null;
	messages: Message[];
	loading: boolean;
	streaming: boolean;
}

const initialState: ChatState = {
	chats: [],
	currentChat: null,
	messages: [],
	loading: false,
	streaming: false
};

function createChatStore() {
	const { subscribe, set, update } = writable<ChatState>(initialState);

	return {
		subscribe,
		set,
		update,
		setLoading(loading: boolean) {
			update((state) => ({ ...state, loading }));
		},
		setStreaming(streaming: boolean) {
			update((state) => ({ ...state, streaming }));
		},
		setChats(chats: Chat[]) {
			update((state) => ({ ...state, chats }));
		},
		setCurrentChat(chat: Chat | null) {
			update((state) => ({ ...state, currentChat: chat }));
		},
		setMessages(messages: Message[]) {
			update((state) => ({ ...state, messages }));
		},
		addMessage(message: Message) {
			update((state) => ({
				...state,
				messages: [...state.messages, message]
			}));
		},
		updateMessage(id: string, content: string) {
			update((state) => ({
				...state,
				messages: state.messages.map((msg) =>
					msg.id === id ? { ...msg, content } : msg
				)
			}));
		},
		clear() {
			set(initialState);
		}
	};
}

export const chatStore = createChatStore();
