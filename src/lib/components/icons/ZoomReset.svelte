<script lang="ts">
	import LocateFixed from 'lucide-svelte/icons/locate-fixed';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<LocateFixed
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
