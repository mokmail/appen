<script lang="ts">
	import BarChart3 from 'lucide-svelte/icons/bar-chart-3';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<BarChart3
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
