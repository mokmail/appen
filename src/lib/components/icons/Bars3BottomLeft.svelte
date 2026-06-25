<script lang="ts">
	import PanelBottom from 'lucide-svelte/icons/panel-bottom';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<PanelBottom
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
