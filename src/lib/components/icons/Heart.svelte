<script lang="ts">
	import Heart from 'lucide-svelte/icons/heart';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Heart
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
