<script lang="ts">
	import Wrench from 'lucide-svelte/icons/wrench';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Wrench
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
