<script lang="ts">
	import Paperclip from 'lucide-svelte/icons/paperclip';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Paperclip
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
