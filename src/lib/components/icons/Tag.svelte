<script lang="ts">
	import Tag from 'lucide-svelte/icons/tag';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Tag
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
