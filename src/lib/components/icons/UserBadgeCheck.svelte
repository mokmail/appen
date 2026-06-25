<script lang="ts">
	import BadgeCheck from 'lucide-svelte/icons/badge-check';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<BadgeCheck
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
