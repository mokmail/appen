<script lang="ts">
	import BookOpen from 'lucide-svelte/icons/book-open';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<BookOpen
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
