<script lang="ts">
	import FilePlus2 from 'lucide-svelte/icons/file-plus-2';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<FilePlus2
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
