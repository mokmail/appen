<script lang="ts">
	import FolderOpen from 'lucide-svelte/icons/folder-open';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<FolderOpen
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
