<script lang="ts">
	import Monitor from 'lucide-svelte/icons/monitor';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Monitor
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
