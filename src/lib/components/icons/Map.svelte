<script lang="ts">
	import Map from 'lucide-svelte/icons/map';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Map
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
