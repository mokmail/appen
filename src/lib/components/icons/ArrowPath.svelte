<script lang="ts">
	import RefreshCw from 'lucide-svelte/icons/refresh-cw';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<RefreshCw
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
