<script lang="ts">
	import PanelLeft from 'lucide-svelte/icons/panel-left';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<PanelLeft
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
