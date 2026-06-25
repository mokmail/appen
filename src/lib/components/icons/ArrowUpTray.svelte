<script lang="ts">
	import Upload from 'lucide-svelte/icons/upload';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Upload
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
