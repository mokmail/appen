<script lang="ts">
	import { toast } from 'svelte-sonner';

	import { getContext } from 'svelte';
	const i18n = getContext('i18n');

	import Modal from '$lib/components/common/Modal.svelte';
	import XMark from '$lib/components/icons/XMark.svelte';
	import CodeBracket from '$lib/components/icons/CodeBracket.svelte';
	import BookOpen from '$lib/components/icons/BookOpen.svelte';
	import { isValidHttpUrl } from '$lib/utils';

	export let show = false;
	export let onSubmit: (e) => void;

	let url = '';
	let accessToken = '';
	let branch = '';
	let ignoredExtensions = '';
	let sourceType: 'repo' | 'wiki' = 'repo';

	const submitHandler = () => {
		const trimmedUrl = url.trim();
		if (!trimmedUrl || !isValidHttpUrl(trimmedUrl)) {
			toast.error($i18n.t('Please enter a valid GitLab URL.'));
			return;
		}

		onSubmit({
			type: sourceType,
			data: {
				url: trimmedUrl,
				accessToken: accessToken.trim() || undefined,
				branch: sourceType === 'repo' ? branch.trim() || undefined : undefined,
				ignoredExtensions: sourceType === 'repo' ? ignoredExtensions.trim() || undefined : undefined
			}
		});
		show = false;
		url = '';
		accessToken = '';
		branch = '';
		ignoredExtensions = '';
	};
</script>

<Modal bind:show size="sm">
	<div class="flex flex-col h-full">
		<div class="flex justify-between items-center dark:text-gray-100 px-5 pt-4 pb-1.5">
			<h1 class="text-lg font-medium self-center font-primary">
				{$i18n.t('Add GitLab Content')}
			</h1>
			<button
				class="self-center"
				aria-label={$i18n.t('Close modal')}
				on:click={() => {
					show = false;
				}}
			>
				<XMark className="size-5" />
			</button>
		</div>

		<div class="px-5 pb-4">
			<form
				on:submit={(e) => {
					e.preventDefault();
					submitHandler();
				}}
			>
				<div class="flex gap-2 mb-4">
					<button
						type="button"
						class={`flex-1 flex items-center justify-center gap-2 px-3 py-2 text-sm rounded-xl transition ${
							sourceType === 'repo'
								? 'bg-black text-white dark:bg-white dark:text-black'
								: 'bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700'
						}`}
						on:click={() => (sourceType = 'repo')}
					>
						<CodeBracket className="size-4" />
						{$i18n.t('Repository')}
					</button>
					<button
						type="button"
						class={`flex-1 flex items-center justify-center gap-2 px-3 py-2 text-sm rounded-xl transition ${
							sourceType === 'wiki'
								? 'bg-black text-white dark:bg-white dark:text-black'
								: 'bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700'
						}`}
						on:click={() => (sourceType = 'wiki')}
					>
						<BookOpen className="size-4" />
						{$i18n.t('Wiki')}
					</button>
				</div>

				<div class="flex justify-between mb-0.5">
					<label for="gitlab-url" class="text-xs text-gray-500"
						>{$i18n.t('GitLab URL')}</label
					>
				</div>
				<input
					id="gitlab-url"
					class="w-full text-sm bg-transparent outline-hidden placeholder:text-gray-300 dark:placeholder:text-gray-700 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 mb-3"
					type="text"
					bind:value={url}
					placeholder={'https://gitlab.com/namespace/project'}
					autocomplete="off"
					required
				/>

				<div class="flex justify-between mb-0.5">
					<label for="gitlab-token" class="text-xs text-gray-500"
						>{$i18n.t('Access Token (optional, for private repos)')}</label
					>
				</div>
				<input
					id="gitlab-token"
					class="w-full text-sm bg-transparent outline-hidden placeholder:text-gray-300 dark:placeholder:text-gray-700 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 mb-3"
					type="password"
					bind:value={accessToken}
					placeholder={$i18n.t('glpat-...')}
					autocomplete="off"
				/>

				{#if sourceType === 'repo'}
					<div class="flex justify-between mb-0.5">
						<label for="gitlab-branch" class="text-xs text-gray-500"
							>{$i18n.t('Branch (optional, defaults to default branch)')}</label
						>
					</div>
					<input
						id="gitlab-branch"
						class="w-full text-sm bg-transparent outline-hidden placeholder:text-gray-300 dark:placeholder:text-gray-700 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 mb-3"
						type="text"
						bind:value={branch}
						placeholder={'main'}
						autocomplete="off"
					/>

					<div class="flex justify-between mb-0.5">
						<label for="gitlab-ignored" class="text-xs text-gray-500"
							>{$i18n.t('Ignore extensions (comma-separated, e.g. png, jpg, svg)')}</label
						>
					</div>
					<input
						id="gitlab-ignored"
						class="w-full text-sm bg-transparent outline-hidden placeholder:text-gray-300 dark:placeholder:text-gray-700 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 mb-3"
						type="text"
						bind:value={ignoredExtensions}
						placeholder={$i18n.t('png, jpg, svg, ico, lock')}
						autocomplete="off"
					/>
				{/if}

				<div class="flex justify-end gap-2 pt-3 bg-gray-50 dark:bg-gray-900/50">
					<button
						class="px-3.5 py-1.5 text-sm font-medium bg-black hover:bg-gray-800 text-white dark:bg-white dark:text-black dark:hover:bg-gray-200 transition rounded-full"
						type="submit"
					>
						{$i18n.t('Add')}
					</button>
				</div>
			</form>
		</div>
	</div>
</Modal>