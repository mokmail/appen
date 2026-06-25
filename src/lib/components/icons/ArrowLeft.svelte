<script lang="ts">
	import ArrowLeft from 'lucide-svelte/icons/arrow-left';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<ArrowLeft
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
