<script lang="ts">
	import AlignJustify from 'lucide-svelte/icons/align-justify';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<AlignJustify
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
