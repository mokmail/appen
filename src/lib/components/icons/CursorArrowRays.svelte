<script lang="ts">
	import MousePointerClick from 'lucide-svelte/icons/mouse-pointer-click';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<MousePointerClick
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
