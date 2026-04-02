// See https://kit.svelte.dev/docs/types#app
declare global {
	namespace App {
		interface Error {
			message: string;
			code?: string;
		}
		interface Locals {
			user?: {
				id: string;
				email: string;
				role: string;
			};
		}
		interface PageData {}
		interface Platform {}
	}
}

export {};
