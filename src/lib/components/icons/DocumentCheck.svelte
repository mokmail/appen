<script lang="ts">
	import FileCheck from 'lucide-svelte/icons/file-check';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<FileCheck
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
