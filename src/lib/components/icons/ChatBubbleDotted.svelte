<script lang="ts">
	import MessageCircleMore from 'lucide-svelte/icons/message-circle-more';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<MessageCircleMore
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
