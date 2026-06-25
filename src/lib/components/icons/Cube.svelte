<script lang="ts">
	import Box from 'lucide-svelte/icons/box';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Box
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
