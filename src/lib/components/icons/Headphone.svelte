<script lang="ts">
	import Headphones from 'lucide-svelte/icons/headphones';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Headphones
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
