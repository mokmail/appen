<script lang="ts">
	import CornerDownRight from 'lucide-svelte/icons/corner-down-right';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<CornerDownRight
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
