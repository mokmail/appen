<script lang="ts">
	import Underline from 'lucide-svelte/icons/underline';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Underline
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
