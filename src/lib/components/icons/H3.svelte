<script lang="ts">
	import Heading3 from 'lucide-svelte/icons/heading-3';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Heading3
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
