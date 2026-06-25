<script lang="ts">
	import MessageSquareCheck from 'lucide-svelte/icons/message-square-check';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<MessageSquareCheck
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
