<script lang="ts">
	import Terminal from 'lucide-svelte/icons/terminal';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Terminal
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
