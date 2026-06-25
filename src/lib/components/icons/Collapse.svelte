<script lang="ts">
	import Minimize2 from 'lucide-svelte/icons/minimize-2';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Minimize2
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
