<script lang="ts">
	import Ellipsis from 'lucide-svelte/icons/ellipsis';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Ellipsis
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
