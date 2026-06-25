<script lang="ts">
	import FileBarChart from 'lucide-svelte/icons/file-bar-chart';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<FileBarChart
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
