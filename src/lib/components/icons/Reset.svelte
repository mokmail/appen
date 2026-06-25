<script lang="ts">
	import RotateCcw from 'lucide-svelte/icons/rotate-ccw';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<RotateCcw
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
