<script lang="ts">
	import Bold from 'lucide-svelte/icons/bold';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Bold
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
