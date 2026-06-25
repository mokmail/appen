<script lang="ts">
	import Pen from 'lucide-svelte/icons/pen';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Pen
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
