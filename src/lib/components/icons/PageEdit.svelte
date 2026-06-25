<script lang="ts">
	import FilePenLine from 'lucide-svelte/icons/file-pen-line';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<FilePenLine
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
