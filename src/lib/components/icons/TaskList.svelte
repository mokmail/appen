<script lang="ts">
	import ListChecks from 'lucide-svelte/icons/list-checks';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<ListChecks
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
