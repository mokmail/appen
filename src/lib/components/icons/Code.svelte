<script lang="ts">
	import SquareCode from 'lucide-svelte/icons/square-code';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<SquareCode
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
