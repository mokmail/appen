<script lang="ts">
	import ArrowLeftFromLine from 'lucide-svelte/icons/arrow-left-from-line';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<ArrowLeftFromLine
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
