<script lang="ts">
	import ArrowRightCircle from 'lucide-svelte/icons/arrow-right-circle';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<ArrowRightCircle
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
