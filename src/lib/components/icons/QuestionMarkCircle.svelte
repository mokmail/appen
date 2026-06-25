<script lang="ts">
	import CircleHelp from 'lucide-svelte/icons/circle-help';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<CircleHelp
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
