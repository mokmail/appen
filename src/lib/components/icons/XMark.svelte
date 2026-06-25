<script lang="ts">
	import X from 'lucide-svelte/icons/x';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<X
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
