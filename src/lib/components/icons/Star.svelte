<script lang="ts">
	import Star from 'lucide-svelte/icons/star';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Star
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
