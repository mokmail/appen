<script lang="ts">
	import CheckSquare from 'lucide-svelte/icons/check-square';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<CheckSquare
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
