<script lang="ts">
	import BookmarkX from 'lucide-svelte/icons/bookmark-x';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<BookmarkX
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
