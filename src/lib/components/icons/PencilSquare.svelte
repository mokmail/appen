<script lang="ts">
	import SquarePen from 'lucide-svelte/icons/square-pen';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<SquarePen
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
