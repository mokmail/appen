<script lang="ts">
	import Maximize from 'lucide-svelte/icons/maximize';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Maximize
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
