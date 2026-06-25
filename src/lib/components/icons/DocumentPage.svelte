<script lang="ts">
	import File from 'lucide-svelte/icons/file';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<File
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
