<script lang="ts">
	import Bookmark from 'lucide-svelte/icons/bookmark';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Bookmark
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
