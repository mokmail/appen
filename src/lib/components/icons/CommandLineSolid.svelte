<script lang="ts">
	import TerminalSquare from 'lucide-svelte/icons/terminal-square';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<TerminalSquare
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
