<script lang="ts">
	import Heading2 from 'lucide-svelte/icons/heading-2';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Heading2
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
