<script lang="ts">
	import ChevronsUpDown from 'lucide-svelte/icons/chevrons-up-down';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<ChevronsUpDown
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
