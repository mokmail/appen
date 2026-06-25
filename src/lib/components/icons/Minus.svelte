<script lang="ts">
	import Minus from 'lucide-svelte/icons/minus';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Minus
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
