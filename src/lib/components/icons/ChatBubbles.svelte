<script lang="ts">
	import MessagesSquare from 'lucide-svelte/icons/messages-square';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<MessagesSquare
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
