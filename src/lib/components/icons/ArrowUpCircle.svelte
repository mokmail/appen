<script lang="ts">
	import ArrowUpCircle from 'lucide-svelte/icons/arrow-up-circle';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<ArrowUpCircle
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
