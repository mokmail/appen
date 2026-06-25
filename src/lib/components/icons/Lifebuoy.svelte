<script lang="ts">
	import LifeBuoy from 'lucide-svelte/icons/life-buoy';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<LifeBuoy
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
