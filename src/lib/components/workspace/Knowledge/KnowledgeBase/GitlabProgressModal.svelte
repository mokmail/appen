<script lang="ts">
	import { getContext } from 'svelte';
	import Modal from '$lib/components/common/Modal.svelte';
	import XMark from '$lib/components/icons/XMark.svelte';
	import Spinner from '$lib/components/common/Spinner.svelte';
	import Check from '$lib/components/icons/Check.svelte';

	const i18n = getContext('i18n');

	export let show = false;
	export let phase: 'idle' | 'fetching' | 'processing' | 'done' | 'error' = 'idle';
	export let current = 0;
	export let total = 0;
	export let filename = '';
	export let successCount = 0;
	export let failCount = 0;
	export let message = '';

	$: progress = total > 0 ? Math.round((current / total) * 100) : 0;
	$: isRunning = phase === 'fetching' || phase === 'processing';
	$: isDone = phase === 'done';
	$: isError = phase === 'error';

	$: phaseLabel = (() => {
		switch (phase) {
			case 'fetching':
				return $i18n.t('Fetching files from GitLab...');
			case 'processing':
				return $i18n.t('Processing files...');
			case 'done':
				return $i18n.t('Import complete');
			case 'error':
				return $i18n.t('Import failed');
			default:
				return '';
		}
	})();
</script>

<Modal bind:show size="sm">
	<div class="flex flex-col h-full">
		<div class="flex justify-between items-center dark:text-gray-100 px-5 pt-4 pb-1.5">
			<h1 class="text-lg font-medium self-center font-primary">
				{#if isDone}
					{$i18n.t('Import Complete')}
				{:else if isError}
					{$i18n.t('Import Failed')}
				{:else}
					{$i18n.t('Importing from GitLab')}
				{/if}
			</h1>
			{#if !isRunning}
				<button
					class="self-center"
					aria-label={$i18n.t('Close modal')}
					on:click={() => (show = false)}
				>
					<XMark className="size-5" />
				</button>
			{/if}
		</div>

		<div class="px-5 pb-5 pt-2 space-y-4">
			<!-- Phase label -->
			<p class="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-2">
				{#if isDone}
					<Check className="size-4 text-green-500" />
				{:else if isError}
					<span class="text-red-500 font-medium">✕</span>
				{/if}
				{phaseLabel}
			</p>

			<!-- Message -->
			{#if message}
				<p class="text-xs text-gray-500 dark:text-gray-500 truncate" title={message}>
					{message}
				</p>
			{/if}

			<!-- Progress bar -->
			{#if phase !== 'idle'}
				<div class="space-y-1.5">
					<div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 overflow-hidden">
						<div
							class="h-2.5 rounded-full transition-all duration-300 ease-in-out"
							class:bg-blue-600={isRunning}
							class:bg-green-500={isDone}
							class:bg-red-500={isError}
							style="width: {isDone ? 100 : isError ? progress : progress}%"
						></div>
					</div>
					{#if total > 0}
						<div class="flex justify-between text-xs text-gray-500 dark:text-gray-400">
							<span>{current}/{total} {$i18n.t('files')}</span>
							<span>{isDone ? '100' : progress}%</span>
						</div>
					{/if}
				</div>
			{/if}

			<!-- Current filename -->
			{#if filename && isRunning}
				<div class="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
					<Spinner className="size-3" />
					<span class="truncate" title={filename}>{$i18n.t('Processing')}: {filename}</span>
				</div>
			{/if}

			<!-- Stats -->
			{#if (successCount > 0 || failCount > 0 || isDone)}
				<div class="grid grid-cols-3 gap-2 pt-2">
					<div class="flex flex-col items-center p-2 bg-gray-50 dark:bg-gray-800 rounded-xl">
						<span class="text-lg font-semibold text-gray-900 dark:text-gray-100">{successCount}</span>
						<span class="text-xs text-gray-500 dark:text-gray-400">{$i18n.t('Succeeded')}</span>
					</div>
					<div class="flex flex-col items-center p-2 bg-gray-50 dark:bg-gray-800 rounded-xl">
						<span class="text-lg font-semibold text-gray-900 dark:text-gray-100">{failCount}</span>
						<span class="text-xs text-gray-500 dark:text-gray-400">{$i18n.t('Failed')}</span>
					</div>
					<div class="flex flex-col items-center p-2 bg-gray-50 dark:bg-gray-800 rounded-xl">
						<span class="text-lg font-semibold text-gray-900 dark:text-gray-100">{total}</span>
						<span class="text-xs text-gray-500 dark:text-gray-400">{$i18n.t('Total')}</span>
					</div>
				</div>
			{/if}

			<!-- Close button when done/error -->
			{#if isDone || isError}
				<div class="flex justify-end pt-2">
					<button
						class="px-3.5 py-1.5 text-sm font-medium bg-black hover:bg-gray-800 text-white dark:bg-white dark:text-black dark:hover:bg-gray-200 transition rounded-full"
						on:click={() => (show = false)}
					>
						{$i18n.t('Close')}
					</button>
				</div>
			{/if}
		</div>
	</div>
</Modal>