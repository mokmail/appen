<script lang="ts">
	import Search from 'lucide-svelte/icons/search';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Search
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
