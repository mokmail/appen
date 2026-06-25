<script lang="ts">
	import Code from 'lucide-svelte/icons/code';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Code
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
