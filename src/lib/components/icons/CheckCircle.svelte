<script lang="ts">
	import CircleCheckBig from 'lucide-svelte/icons/circle-check-big';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<CircleCheckBig
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
