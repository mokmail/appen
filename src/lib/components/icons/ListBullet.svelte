<script lang="ts">
	import List from 'lucide-svelte/icons/list';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<List
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
