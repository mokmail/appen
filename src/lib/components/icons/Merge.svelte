<script lang="ts">
	import GitMerge from 'lucide-svelte/icons/git-merge';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<GitMerge
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
