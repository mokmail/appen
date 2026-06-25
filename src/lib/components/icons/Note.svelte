<script lang="ts">
	import FileText from 'lucide-svelte/icons/file-text';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<FileText
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
