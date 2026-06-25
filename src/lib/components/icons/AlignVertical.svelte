<script lang="ts">
	import AlignVerticalJustifyCenter from 'lucide-svelte/icons/align-vertical-justify-center';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<AlignVerticalJustifyCenter
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
