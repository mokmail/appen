<script lang="ts">
	import FileDown from 'lucide-svelte/icons/file-down';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<FileDown
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
