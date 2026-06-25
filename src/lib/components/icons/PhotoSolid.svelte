<script lang="ts">
	import Image from 'lucide-svelte/icons/image';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Image
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
