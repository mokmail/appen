<script lang="ts">
	import Folder from 'lucide-svelte/icons/folder';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Folder
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
