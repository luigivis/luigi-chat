<script lang="ts">
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	import { getUsers, createUser, updateUser, deleteUser, type User } from '$lib/apis/users';
	import { Trash2, Edit, UserPlus, X, Check } from 'lucide-svelte';

	let users: User[] = [];
	let loading = true;
	let error = '';
	let showCreateModal = false;
	let showEditModal = false;

	let newUser = { email: '', password: '', role: 'user' };
	let editingUser: User | null = null;

	const roleOptions = ['user', 'admin'];
	const statusOptions = ['active', 'inactive', 'suspended'];

	onMount(async () => {
		if (!$authStore.user || $authStore.user.role !== 'admin') {
			goto('/');
			return;
		}
		await loadUsers();
	});

	async function loadUsers() {
		loading = true;
		error = '';
		try {
			users = await getUsers();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load users';
		} finally {
			loading = false;
		}
	}

	async function handleCreate() {
		try {
			await createUser(newUser);
			showCreateModal = false;
			newUser = { email: '', password: '', role: 'user' };
			await loadUsers();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to create user';
		}
	}

	async function handleUpdate() {
		if (!editingUser) return;
		try {
			await updateUser(editingUser.id, {
				role: editingUser.role,
				status: editingUser.status
			});
			showEditModal = false;
			editingUser = null;
			await loadUsers();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to update user';
		}
	}

	async function handleDelete(userId: string) {
		if (!confirm('Are you sure you want to delete this user?')) return;
		try {
			await deleteUser(userId);
			await loadUsers();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to delete user';
		}
	}

	function openEdit(user: User) {
		editingUser = { ...user };
		showEditModal = true;
	}
</script>

<div class="p-6 max-w-6xl mx-auto">
	<div class="flex items-center justify-between mb-6">
		<h1 class="text-2xl font-bold">User Management</h1>
		<button
			on:click={() => (showCreateModal = true)}
			class="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition"
		>
			<UserPlus size={18} />
			Add User
		</button>
	</div>

	{#if error}
		<div class="mb-4 p-4 bg-red-900/50 border border-red-700 rounded-lg text-red-200">
			{error}
		</div>
	{/if}

	{#if loading}
		<div class="text-center py-12 text-gray-400">Loading users...</div>
	{:else}
		<div class="bg-gray-800 rounded-lg overflow-hidden">
			<table class="w-full">
				<thead class="bg-gray-900">
					<tr>
						<th class="px-4 py-3 text-left text-sm font-semibold text-gray-300">Email</th>
						<th class="px-4 py-3 text-left text-sm font-semibold text-gray-300">Role</th>
						<th class="px-4 py-3 text-left text-sm font-semibold text-gray-300">Status</th>
						<th class="px-4 py-3 text-left text-sm font-semibold text-gray-300">Default Model</th>
						<th class="px-4 py-3 text-left text-sm font-semibold text-gray-300">API Key</th>
						<th class="px-4 py-3 text-right text-sm font-semibold text-gray-300">Actions</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-gray-700">
					{#each users as user}
						<tr class="hover:bg-gray-750">
							<td class="px-4 py-3">{user.email}</td>
							<td class="px-4 py-3">
								<span
									class="px-2 py-1 text-xs rounded-full {user.role === 'admin'
										? 'bg-purple-600'
										: 'bg-gray-600'}"
								>
									{user.role}
								</span>
							</td>
							<td class="px-4 py-3">
								<span
									class="px-2 py-1 text-xs rounded-full {user.status === 'active'
										? 'bg-green-600'
										: user.status === 'inactive'
											? 'bg-yellow-600'
											: 'bg-red-600'}"
								>
									{user.status}
								</span>
							</td>
							<td class="px-4 py-3 text-sm text-gray-400">{user.default_model || '-'}</td>
							<td class="px-4 py-3 font-mono text-xs text-gray-400">
								{user.litellm_key ? `${user.litellm_key.slice(0, 20)}...` : '-'}
							</td>
							<td class="px-4 py-3 text-right">
								<button
									on:click={() => openEdit(user)}
									class="p-2 hover:bg-gray-700 rounded transition"
									title="Edit"
								>
									<Edit size={16} />
								</button>
								<button
									on:click={() => handleDelete(user.id)}
									class="p-2 hover:bg-red-700 rounded transition text-red-400"
									title="Delete"
								>
									<Trash2 size={16} />
								</button>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>

{#if showCreateModal}
	<div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
		<div class="bg-gray-800 rounded-lg p-6 w-full max-w-md">
			<div class="flex items-center justify-between mb-4">
				<h2 class="text-xl font-bold">Create User</h2>
				<button on:click={() => (showCreateModal = false)} class="p-1 hover:bg-gray-700 rounded">
					<X size={20} />
				</button>
			</div>

			<form on:submit|preventDefault={handleCreate} class="space-y-4">
				<div>
					<label class="block text-sm text-gray-400 mb-1">Email</label>
					<input
						type="email"
						bind:value={newUser.email}
						required
						class="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
					/>
				</div>

				<div>
					<label class="block text-sm text-gray-400 mb-1">Password</label>
					<input
						type="password"
						bind:value={newUser.password}
						required
						class="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
					/>
				</div>

				<div>
					<label class="block text-sm text-gray-400 mb-1">Role</label>
					<select
						bind:value={newUser.role}
						class="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
					>
						{#each roleOptions as role}
							<option value={role}>{role}</option>
						{/each}
					</select>
				</div>

				<div class="flex gap-3 pt-2">
					<button
						type="submit"
						class="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition"
					>
						<Check size={18} />
						Create
					</button>
					<button
						type="button"
						on:click={() => (showCreateModal = false)}
						class="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition"
					>
						Cancel
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}

{#if showEditModal && editingUser}
	<div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
		<div class="bg-gray-800 rounded-lg p-6 w-full max-w-md">
			<div class="flex items-center justify-between mb-4">
				<h2 class="text-xl font-bold">Edit User</h2>
				<button on:click={() => (showEditModal = false)} class="p-1 hover:bg-gray-700 rounded">
					<X size={20} />
				</button>
			</div>

			<form on:submit|preventDefault={handleUpdate} class="space-y-4">
				<div>
					<label class="block text-sm text-gray-400 mb-1">Email</label>
					<input
						type="email"
						value={editingUser.email}
						disabled
						class="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg opacity-60"
					/>
				</div>

				<div>
					<label class="block text-sm text-gray-400 mb-1">Role</label>
					<select
						bind:value={editingUser.role}
						class="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
					>
						{#each roleOptions as role}
							<option value={role}>{role}</option>
						{/each}
					</select>
				</div>

				<div>
					<label class="block text-sm text-gray-400 mb-1">Status</label>
					<select
						bind:value={editingUser.status}
						class="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
					>
						{#each statusOptions as status}
							<option value={status}>{status}</option>
						{/each}
					</select>
				</div>

				<div class="flex gap-3 pt-2">
					<button
						type="submit"
						class="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition"
					>
						<Check size={18} />
						Save
					</button>
					<button
						type="button"
						on:click={() => (showEditModal = false)}
						class="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition"
					>
						Cancel
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}