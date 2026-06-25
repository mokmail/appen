<script lang="ts">
	import Check from 'lucide-svelte/icons/check';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Check
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
