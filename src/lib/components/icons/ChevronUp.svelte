<script lang="ts">
	import ChevronUp from 'lucide-svelte/icons/chevron-up';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<ChevronUp
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
