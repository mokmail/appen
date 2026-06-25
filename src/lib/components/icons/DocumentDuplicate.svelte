<script lang="ts">
	import Files from 'lucide-svelte/icons/files';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Files
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
