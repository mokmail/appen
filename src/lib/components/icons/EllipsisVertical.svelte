<script lang="ts">
	import EllipsisVertical from 'lucide-svelte/icons/ellipsis-vertical';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<EllipsisVertical
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
