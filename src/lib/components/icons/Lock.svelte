<script lang="ts">
	import Lock from 'lucide-svelte/icons/lock';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Lock
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
