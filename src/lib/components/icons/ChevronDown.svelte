<script lang="ts">
	import ChevronDown from 'lucide-svelte/icons/chevron-down';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<ChevronDown
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
