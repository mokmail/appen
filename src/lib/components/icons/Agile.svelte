<script lang="ts">
	import Workflow from 'lucide-svelte/icons/workflow';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Workflow
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
