<script lang="ts">
	import MessageSquarePlus from 'lucide-svelte/icons/message-square-plus';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<MessageSquarePlus
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
