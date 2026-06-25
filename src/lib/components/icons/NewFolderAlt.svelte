<script lang="ts">
	import FolderPlus from 'lucide-svelte/icons/folder-plus';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<FolderPlus
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
