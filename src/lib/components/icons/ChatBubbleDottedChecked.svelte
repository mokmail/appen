<script lang="ts">
	import MessageCircleCheck from 'lucide-svelte/icons/message-circle-check';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<MessageCircleCheck
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
